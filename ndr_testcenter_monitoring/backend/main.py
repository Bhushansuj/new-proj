import os
from datetime import datetime, timedelta
from typing import Optional
from database import get_connection
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="NDR Testcenter Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "ndr_super_secret_key")
AGENT_API_TOKEN = os.getenv("AGENT_API_TOKEN", "ndr-agent-token")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Login erforderlich")

    token = authorization.replace("Bearer ", "", 1)

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Ungültiger Login-Token")


def require_admin(authorization: str = Header(default="")):
    payload = decode_token(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur Admin darf diese Aktion ausführen")
    return payload


def require_admin_or_mitarbeiter(authorization: str = Header(default="")):
    payload = decode_token(authorization)
    if payload.get("role") not in ("admin", "mitarbeiter"):
        raise HTTPException(status_code=403, detail="Keine Berechtigung für diese Aktion")
    return payload


def verify_password(password: str, stored_password: str):
    if stored_password.startswith("$2"):
        return pwd_context.verify(password, stored_password)
    return password == stored_password


def get_table_columns(cursor, table_name: str):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = set()

    for row in cursor.fetchall():
        if isinstance(row, dict):
            columns.add(row["Field"])
        else:
            columns.add(row[0])

    return columns


def optional_system_select(columns, column_name: str):
    if column_name in columns:
        return f"systems.{column_name}"
    return f"NULL AS {column_name}"


def system_values(system: "System"):
    return {
        "hostname": system.hostname,
        "system_type": system.system_type,
        "mac_address": system.mac_address,
        "model": system.model,
        "location": system.location,
        "inventory_number": system.inventory_number,
        "os_version": system.os_version,
        "gpu": system.gpu,
        "current_usage": system.current_usage,
        "reserved_until": system.reserved_until,
        "reinstalled_at": system.reinstalled_at,
        "info": system.info,
        "helpline": system.helpline,
    }


def sync_system_status(cursor):
    cursor.execute(
        """
        UPDATE system_status
        SET power_status = 'offline'
        WHERE last_seen IS NOT NULL
          AND last_seen < (NOW() - INTERVAL 5 MINUTE)
        """
    )
    system_columns = get_table_columns(cursor, "systems")

    if "reserved_until" in system_columns:
        cursor.execute(
            """
            UPDATE systems s
            LEFT JOIN (
                SELECT system_id, MAX(reserved_until) AS reserved_until
                FROM reservations
                WHERE reserved_until >= NOW()
                GROUP BY system_id
            ) active_reservations ON s.id = active_reservations.system_id
            SET s.reserved_until = active_reservations.reserved_until
            """
        )

    if "current_usage" in system_columns:
        cursor.execute(
            """
            UPDATE systems s
            LEFT JOIN (
                SELECT r.system_id, r.purpose
                FROM reservations r
                JOIN (
                    SELECT system_id, MAX(reserved_until) AS reserved_until
                    FROM reservations
                    WHERE reserved_until >= NOW()
                    GROUP BY system_id
                ) latest
                    ON r.system_id = latest.system_id
                   AND r.reserved_until = latest.reserved_until
            ) active_reservations ON s.id = active_reservations.system_id
            SET s.current_usage = COALESCE(active_reservations.purpose, s.current_usage)
            """
        )
    cursor.execute(
        """
        UPDATE system_status ss
        JOIN reservations r ON ss.system_id = r.system_id
        SET ss.usage_status = 'reserved'
        WHERE r.reserved_until >= NOW()
        """
    )
    cursor.execute(
        """
        UPDATE system_status ss
        LEFT JOIN reservations r
            ON ss.system_id = r.system_id
           AND r.reserved_until >= NOW()
        SET ss.usage_status = 'free'
        WHERE ss.usage_status = 'reserved'
          AND r.id IS NULL
        """
    )


def safe_sync_system_status(cursor):
    try:
        sync_system_status(cursor)
    except Exception as error:
        print("Status sync skipped:", error)


class LoginData(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "mitarbeiter"


class System(BaseModel):
    hostname: str
    system_type: str = "client"
    mac_address: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    inventory_number: Optional[str] = None
    os_version: Optional[str] = None
    gpu: Optional[str] = None
    current_usage: Optional[str] = None
    reserved_until: Optional[str] = None
    reinstalled_at: Optional[str] = None
    info: Optional[str] = None
    helpline: Optional[str] = None


class Reservation(BaseModel):
    system_id: int
    user_id: int
    reserved_from: str
    reserved_until: str
    purpose: str


class AgentStatus(BaseModel):
    hostname: str
    power_status: str = "online"
    usage_status: str = "busy"
    windows_version: Optional[str] = None
    reinstalled_at: Optional[str] = None
    last_user: Optional[str] = None
    last_seen: Optional[str] = None


@app.get("/")
def home():
    return {"message": "NDR Testcenter Monitoring API läuft"}


@app.post("/login")
def login(login_data: LoginData):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT users.*, roles.role_name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE username = %s
        """,
        (login_data.username,),
    )
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Benutzername oder Passwort ist falsch")

    token = create_access_token({"user_id": user["id"], "role": user["role_name"]})
    return {"access_token": token, "role": user["role_name"], "user_id": user["id"]}


@app.get("/systems")
def get_systems():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    safe_sync_system_status(cursor)
    connection.commit()
    system_columns = get_table_columns(cursor, "systems")

    cursor.execute(
        f"""
        SELECT
            systems.id,
            systems.hostname,
            systems.system_type,
            systems.mac_address,
            systems.model,
            systems.location,
            systems.inventory_number,
            {optional_system_select(system_columns, "os_version")},
            {optional_system_select(system_columns, "gpu")},
            {optional_system_select(system_columns, "current_usage")},
            {optional_system_select(system_columns, "reserved_until")},
            {optional_system_select(system_columns, "reinstalled_at")},
            {optional_system_select(system_columns, "info")},
            {optional_system_select(system_columns, "helpline")},
            COALESCE(system_status.power_status, 'offline') AS power_status,
            COALESCE(system_status.usage_status, 'free') AS usage_status,
            system_status.windows_version,
            system_status.last_user,
            system_status.last_seen
        FROM systems
        LEFT JOIN system_status ON systems.id = system_status.system_id
        ORDER BY systems.system_type, systems.hostname
        """
    )
    systems = cursor.fetchall()

    cursor.close()
    connection.close()
    return systems


@app.post("/systems")
def add_system(system: System, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    system_columns = get_table_columns(cursor, "systems")

    values_by_column = system_values(system)
    insert_columns = [column for column in values_by_column if column in system_columns]
    placeholders = ", ".join(["%s"] * len(insert_columns))
    column_names = ", ".join(insert_columns)

    cursor.execute(
        f"INSERT INTO systems ({column_names}) VALUES ({placeholders})",
        tuple(values_by_column[column] for column in insert_columns),
    )
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "System erfolgreich hinzugefügt"}


@app.put("/systems/{system_id}")
def update_system(system_id: int, system: System, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    system_columns = get_table_columns(cursor, "systems")

    values_by_column = system_values(system)
    update_columns = [column for column in values_by_column if column in system_columns]
    assignments = ", ".join([f"{column} = %s" for column in update_columns])
    values = [values_by_column[column] for column in update_columns]
    values.append(system_id)

    cursor.execute(
        f"UPDATE systems SET {assignments} WHERE id = %s",
        tuple(values),
    )
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "System wurde aktualisiert"}


@app.post("/systems/{system_id}/reserve")
def reserve_system(system_id: int, authorization: str = Header(default="")):
    decode_token(authorization)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO system_status (system_id, usage_status)
        VALUES (%s, 'reserved')
        ON DUPLICATE KEY UPDATE usage_status = 'reserved'
        """,
        (system_id,),
    )
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "System wurde reserviert"}


@app.post("/systems/{system_id}/release")
def release_system(system_id: int, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO system_status (system_id, usage_status)
        VALUES (%s, 'free')
        ON DUPLICATE KEY UPDATE usage_status = 'free'
        """,
        (system_id,),
    )
    system_columns = get_table_columns(cursor, "systems")

    if "reserved_until" in system_columns:
        cursor.execute("UPDATE systems SET reserved_until = NULL WHERE id = %s", (system_id,))

    if "current_usage" in system_columns:
        cursor.execute("UPDATE systems SET current_usage = 'Frei' WHERE id = %s", (system_id,))

    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "System wurde freigegeben"}


@app.post("/systems/{system_id}/power")
def toggle_power_status(system_id: int, authorization: str = Header(default="")):
    decode_token(authorization)
 
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT power_status FROM system_status WHERE system_id = %s",
        (system_id,),
    )
    status = cursor.fetchone()
    current_power = status["power_status"] if status else "offline"
    next_power = "offline" if current_power == "online" else "online"

    cursor.execute(
        """
        INSERT INTO system_status (system_id, power_status, last_seen)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            power_status = VALUES(power_status),
            last_seen = VALUES(last_seen)
        """,
        (system_id, next_power),
    )
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": f"Power wurde auf {next_power} gesetzt", "power_status": next_power}


@app.delete("/systems/{system_id}")
def delete_system(system_id: int, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM reservations WHERE system_id = %s", (system_id,))
    cursor.execute("DELETE FROM system_status WHERE system_id = %s", (system_id,))
    cursor.execute("DELETE FROM systems WHERE id = %s", (system_id,))
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "System wurde gelöscht"}


@app.post("/reservations")
def create_reservation(reservation: Reservation, authorization: str = Header(default="")):
    decode_token(authorization)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reservations
        (system_id, user_id, reserved_from, reserved_until, purpose)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            reservation.system_id,
            reservation.user_id,
            reservation.reserved_from,
            reservation.reserved_until,
            reservation.purpose,
        ),
    )
    cursor.execute(
        """
        INSERT INTO system_status (system_id, usage_status)
        VALUES (%s, 'reserved')
        ON DUPLICATE KEY UPDATE usage_status = 'reserved'
        """,
        (reservation.system_id,),
    )
    system_columns = get_table_columns(cursor, "systems")

    if "reserved_until" in system_columns:
        cursor.execute(
            "UPDATE systems SET reserved_until = %s WHERE id = %s",
            (reservation.reserved_until, reservation.system_id),
        )

    if "current_usage" in system_columns:
        cursor.execute(
            "UPDATE systems SET current_usage = %s WHERE id = %s",
            (reservation.purpose, reservation.system_id),
        )

    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "Reservierung erfolgreich erstellt"}


@app.get("/reservations")
def get_reservations():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    safe_sync_system_status(cursor)
    connection.commit()

    cursor.execute(
        """
        SELECT
            reservations.id,
            reservations.system_id,
            systems.hostname,
            users.username,
            reservations.reserved_from,
            reservations.reserved_until,
            reservations.purpose
        FROM reservations
        JOIN systems ON reservations.system_id = systems.id
        JOIN users ON reservations.user_id = users.id
        WHERE reservations.reserved_until >= NOW()
        ORDER BY reservations.reserved_until DESC
        """
    )
    reservations = cursor.fetchall()

    cursor.close()
    connection.close()
    return reservations


@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT system_id FROM reservations WHERE id = %s", (reservation_id,))
    reservation = cursor.fetchone()
    cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))

    if reservation:
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM reservations
            WHERE system_id = %s
        """,
            (reservation["system_id"],),
        )
        remaining = cursor.fetchone()

        if remaining["count"] == 0:
            cursor.execute(
                """
                INSERT INTO system_status (system_id, usage_status)
                VALUES (%s, 'free')
                ON DUPLICATE KEY UPDATE usage_status = 'free'
                """,
                (reservation["system_id"],),
            )
            system_columns = get_table_columns(cursor, "systems")

            if "reserved_until" in system_columns:
                cursor.execute(
                    "UPDATE systems SET reserved_until = NULL WHERE id = %s",
                    (reservation["system_id"],),
                )

            if "current_usage" in system_columns:
                cursor.execute(
                    "UPDATE systems SET current_usage = 'Frei' WHERE id = %s",
                    (reservation["system_id"],),
                )

    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "Reservierung wurde gelöscht"}


@app.get("/users")
def get_users(authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT users.id, users.username, roles.role_name
        FROM users
        LEFT JOIN roles ON users.role_id = roles.id
        ORDER BY users.username
        """
    )
    users = cursor.fetchall()

    cursor.close()
    connection.close()
    return users


@app.post("/users")
def create_user(user: UserCreate, authorization: str = Header(default="")):
    require_admin(authorization)

    if user.role not in ("admin", "mitarbeiter"):
        raise HTTPException(status_code=400, detail="Rolle muss admin oder mitarbeiter sein")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id FROM roles WHERE role_name = %s", (user.role,))
    role_row = cursor.fetchone()

    if not role_row:
        cursor.execute("INSERT INTO roles (role_name) VALUES (%s)", (user.role,))
        connection.commit()
        role_id = cursor.lastrowid
    else:
        role_id = role_row["id"]

    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role_id)
        VALUES (%s, %s, %s)
        """,
        (user.username, user.password, role_id),
    )
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "Benutzer wurde erstellt"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, authorization: str = Header(default="")):
    require_admin(authorization)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "Benutzer wurde gelöscht"}


@app.post("/agent/status")
def receive_agent_status(status: AgentStatus, x_api_token: str = Header(default="")):
    if x_api_token != AGENT_API_TOKEN:
        raise HTTPException(status_code=401, detail="Ungültiger Agent API-Token")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id FROM systems WHERE hostname = %s", (status.hostname,))
    system = cursor.fetchone()

    if not system:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="System nicht gefunden")

    last_seen = status.last_seen or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO system_status
        (system_id, power_status, usage_status, windows_version, last_user, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            power_status = VALUES(power_status),
            usage_status = VALUES(usage_status),
            windows_version = VALUES(windows_version),
            last_user = VALUES(last_user),
            last_seen = VALUES(last_seen)
        """,
        (
            system["id"],
            status.power_status,
            status.usage_status,
            status.windows_version,
            status.last_user,
            last_seen,
        ),
    )

    if status.reinstalled_at:
        cursor.execute(
            """
            UPDATE systems
            SET reinstalled_at = %s
            WHERE id = %s
            """,
            (status.reinstalled_at, system["id"]),
        )

    connection.commit()

    cursor.close()
    connection.close()
    return {"message": "Agent status received"}
