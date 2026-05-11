const API_URL = "http://127.0.0.1:8000";

let systemsData = [];
let hiddenDashboardSystemIds = JSON.parse(
    localStorage.getItem("hiddenDashboardSystemIds") || "[]"
);
let dashboardFilter = "all";
const token = localStorage.getItem("accessToken");
const role = localStorage.getItem("role");

function applyTheme() {
    const theme = localStorage.getItem("theme") || "light";
    document.body.classList.toggle("dark-mode", theme === "dark");

    document.querySelectorAll('[onclick="toggleTheme()"]').forEach((button) => {
        button.innerText = theme === "dark" ? "Light Mode" : "Dark Mode";
    });
}

function toggleTheme() {
    const currentTheme = localStorage.getItem("theme") || "light";
    localStorage.setItem("theme", currentTheme === "dark" ? "light" : "dark");
    applyTheme();
}

function authHeaders() {
    return token ? { Authorization: `Bearer ${token}` } : {};
}

function requireLogin() {
    const page = window.location.pathname.split("/").pop() || "index.html";

    if (page === "login.html") {
        return;
    }

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    if (role === "mitarbeiter" && !["reservations.html", "systems.html"].includes(page)) {
        window.location.href = "reservations.html";
    }
}

function applyRoleUi() {
    if (!token) {
        return;
    }

    if (role !== "admin") {
        document.querySelectorAll(".admin-only").forEach((element) => {
            element.style.display = "none";
        });
    }

    if (role === "mitarbeiter") {
        document.querySelectorAll('a[href="index.html"], a[href="users.html"]').forEach((link) => {
            link.style.display = "none";
        });
    }
}

async function login(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const error = document.getElementById("loginError");

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
        const result = await response.json();

        if (!response.ok || !result.access_token) {
            error.innerText = result.detail || result.error || "Login fehlgeschlagen";
            return;
        }

        localStorage.setItem("accessToken", result.access_token);
        localStorage.setItem("role", result.role);
        localStorage.setItem("userId", result.user_id);
        window.location.href = result.role === "mitarbeiter" ? "reservations.html" : "index.html";
    } catch (loginError) {
        error.innerText = "Backend nicht erreichbar";
    }
}

function logout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("role");
    localStorage.removeItem("userId");
    window.location.href = "login.html";
}

function text(value) {
    return value || "-";
}

function normalize(value) {
    return String(value || "").toLowerCase();
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }

    const normalized = String(value).replace("T", " ");
    const date = new Date(normalized);

    if (Number.isNaN(date.getTime())) {
        return normalized;
    }

    return date.toLocaleString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function minutesSince(value) {
    if (!value) {
        return null;
    }

    const date = new Date(String(value).replace(" ", "T"));

    if (Number.isNaN(date.getTime())) {
        return null;
    }

    return Math.floor((Date.now() - date.getTime()) / 60000);
}

function formatLastSeen(value) {
    const minutes = minutesSince(value);

    if (minutes === null) {
        return "nie gesehen";
    }

    if (minutes < 1) {
        return "gerade eben";
    }

    if (minutes === 1) {
        return "vor 1 Minute";
    }

    if (minutes < 60) {
        return `vor ${minutes} Minuten`;
    }

    const hours = Math.floor(minutes / 60);
    return hours === 1 ? "vor 1 Stunde" : `vor ${hours} Stunden`;
}

function csvValue(value) {
    const safeValue = String(value ?? "").replaceAll('"', '""');
    return `"${safeValue}"`;
}

function exportSystemsCsv() {
    if (!systemsData.length) {
        alert("Keine Systemdaten zum Exportieren vorhanden.");
        return;
    }

    const headers = [
        "Hostname",
        "Typ",
        "MAC-Adresse",
        "OS",
        "Modell",
        "Standort",
        "Verwendung",
        "Reserviert bis",
        "Power",
        "Status",
        "Letzter Benutzer",
        "Letzter Agent-Kontakt",
    ];
    const rows = systemsData.map((system) => [
        system.hostname,
        system.system_type,
        system.mac_address,
        system.os_version || system.windows_version,
        system.model,
        system.location,
        system.current_usage,
        formatDateTime(system.reserved_until),
        getEffectivePowerStatus(system),
        getUsageStatus(system),
        system.last_user,
        formatLastSeen(system.last_seen),
    ]);
    const csv = [
        headers.map(csvValue).join(";"),
        ...rows.map((row) => row.map(csvValue).join(";")),
    ].join("\r\n");
    const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const date = new Date().toISOString().slice(0, 10);

    link.href = url;
    link.download = `ndr-testcenter-systeme-${date}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function getEffectivePowerStatus(system) {
    const minutes = minutesSince(system.last_seen);

    if (minutes !== null && minutes > 5) {
        return "offline";
    }

    return system.power_status || "offline";
}

function getUsageStatus(system) {
    const usage = normalize(system.current_usage);
    const status = normalize(system.usage_status);

    if (status === "reserved" || usage.includes("reserv")) {
        return "reserved";
    }

    if (status === "busy" || (system.current_usage && usage !== "frei")) {
        return "busy";
    }

    return "free";
}

function matchesDashboardFilter(system) {
    const usageStatus = getUsageStatus(system);
    const powerStatus = getEffectivePowerStatus(system);

    if (dashboardFilter === "all") {
        return true;
    }

    if (dashboardFilter === "online" || dashboardFilter === "offline") {
        return powerStatus === dashboardFilter;
    }

    return usageStatus === dashboardFilter;
}

function setDashboardFilter(filter, button) {
    dashboardFilter = filter;
    document.querySelectorAll(".filter-btn").forEach((item) => item.classList.remove("active"));

    if (button) {
        button.classList.add("active");
    }

    filterSystems();
}

async function loadSystems() {
    try {
        const response = await fetch(`${API_URL}/systems`);

        if (!response.ok) {
            console.error("Systeme konnten nicht geladen werden:", await response.text());
            alert("Status konnte nicht geprüft werden. Backend oder Datenbank prüfen.");
            return;
        }

        systemsData = await response.json();

        renderSystems(systemsData);
        updateCards(systemsData);
    } catch (error) {
        console.error("Fehler beim Laden der Systeme:", error);
    }
}

async function checkStatus() {
    await loadSystems();
    alert("Status wurde geprüft.");
}

async function loadReservations() {
    const table = document.getElementById("reservationsTable");

    if (!table) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/reservations`);

        if (!response.ok) {
            console.error("Reservierungen konnten nicht geladen werden:", await response.text());
            return;
        }

        const reservations = await response.json();

        table.innerHTML = "";

        if (!reservations.length) {
            table.innerHTML = `<tr><td colspan="6">Keine Reservierungen vorhanden.</td></tr>`;
            return;
        }

        reservations.forEach((reservation) => {
            table.innerHTML += `
                <tr>
                    <td>${text(reservation.hostname)}</td>
                    <td>${text(reservation.username)}</td>
                    <td>${formatDateTime(reservation.reserved_from)}</td>
                    <td>${formatDateTime(reservation.reserved_until)}</td>
                    <td>${text(reservation.purpose)}</td>
                    <td>
                        <button class="delete-btn" onclick="deleteReservation(${reservation.id})">
                            Löschen
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Fehler beim Laden der Reservierungen:", error);
    }
}

async function loadUsers() {
    const table = document.getElementById("usersTable");

    if (!table) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/users`, { headers: authHeaders() });

        if (!response.ok) {
            console.error("Benutzer konnten nicht geladen werden:", await response.text());
            return;
        }

        const users = await response.json();

        table.innerHTML = "";

        if (!users.length) {
            table.innerHTML = `<tr><td colspan="3">Keine Benutzer vorhanden.</td></tr>`;
            return;
        }

        users.forEach((user) => {
            table.innerHTML += `
                <tr>
                    <td>${text(user.username)}</td>
                    <td>${text(user.role_name)}</td>
                    <td>
                        <button class="delete-btn" onclick="deleteUser(${user.id})">
                            Löschen
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
    }
}

function openUserModal() {
    const modal = document.getElementById("userModal");

    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeUserModal() {
    const modal = document.getElementById("userModal");

    if (modal) {
        modal.classList.add("hidden");
    }
}

async function createUser(event) {
    event.preventDefault();

    const data = {
        username: document.getElementById("newUsername").value,
        password: document.getElementById("newPassword").value,
        role: document.getElementById("newRole").value,
    };

    try {
        const response = await fetch(`${API_URL}/users`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify(data),
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || "Benutzer konnte nicht erstellt werden");
            return;
        }

        alert(result.message);
        event.target.reset();
        closeUserModal();
        loadUsers();
    } catch (error) {
        console.error(error);
    }
}

function renderSystems(systems) {
    const table = document.getElementById("systemsTable");

    if (!table) {
        return;
    }

    table.innerHTML = "";
    const visibleSystems = table.dataset.view === "dashboard"
        ? systems.filter((system) => !hiddenDashboardSystemIds.includes(system.id) && matchesDashboardFilter(system))
        : systems;

    visibleSystems.forEach((system) => {
        const status = getUsageStatus(system);
        const powerStatus = getEffectivePowerStatus(system);
        const agentClass = minutesSince(system.last_seen) !== null && minutesSince(system.last_seen) <= 5
            ? "agent-fresh"
            : "agent-stale";
        const actionButton = role === "admin" && status === "reserved"
            ? `<button class="release-btn" onclick="releaseSystem(${system.id})">Freigeben</button>`
            : `<button class="reserve-btn" onclick="reserveSystem(${system.id})">Reservieren</button>`;
        const deleteColumn = role === "admin"
            ? `<td class="admin-only"><button class="delete-btn" onclick="deleteSystem(${system.id})">Löschen</button></td>`
            : "";
        const editColumn = role === "admin"
            ? `<td class="admin-only"><button class="secondary-btn small-btn" onclick="openSystemEditModal(${system.id})">Bearbeiten</button></td>`
            : "";

        if (table.dataset.view === "dashboard") {
            table.innerHTML += `
                <tr>
                    <td>${text(system.hostname)}</td>
                    <td>${text(system.mac_address)}</td>
                    <td>${text(system.os_version || system.windows_version)}</td>
                    <td>${text(system.model)}</td>
                    <td>
                        <button class="power power-toggle ${powerStatus}" onclick="togglePower(${system.id})">
                            ${text(powerStatus)}
                        </button>
                    </td>
                    <td><span class="agent ${agentClass}">${formatLastSeen(system.last_seen)}</span></td>
                    <td>${actionButton}</td>
                    <td>
                        <button class="delete-btn" onclick="removeFromDashboard(${system.id})">
                            Entfernen
                        </button>
                    </td>
                </tr>
            `;
            return;
        }

        const colspan = role === "admin" ? 11 : 9;
        const row = `
            <tr>
                <td>${text(system.hostname)}</td>
                <td>${text(system.mac_address)}</td>
                <td>${text(system.os_version || system.windows_version)}</td>
                <td>${text(system.model)}</td>
                <td>${text(system.location)}</td>
                <td>
                    <button class="power power-toggle ${powerStatus}" onclick="togglePower(${system.id})">
                        ${text(powerStatus)}
                    </button>
                </td>
                <td><span class="status ${status}">${status}</span></td>
                <td>${actionButton}</td>
                ${editColumn}
                ${deleteColumn}
                <td>
                    <button class="icon-btn" onclick="toggleSystemDetails(${system.id})" aria-label="Details anzeigen">
                        ▾
                    </button>
                </td>
            </tr>
            <tr id="details-${system.id}" class="details-row hidden">
                <td colspan="${colspan}">
                    <div class="details-grid">
                        <div><strong>Typ</strong><span>${text(system.system_type)}</span></div>
                        <div><strong>Verwendung</strong><span>${text(system.current_usage)}</span></div>
                        <div><strong>Reserviert bis</strong><span>${formatDateTime(system.reserved_until)}</span></div>
                        <div><strong>Letzter Benutzer</strong><span>${text(system.last_user)}</span></div>
                        <div><strong>Agent</strong><span>${formatLastSeen(system.last_seen)}</span></div>
                    </div>
                </td>
            </tr>
        `;

        table.innerHTML += row;
    });
}

function toggleSystemDetails(systemId) {
    const row = document.getElementById(`details-${systemId}`);

    if (row) {
        row.classList.toggle("hidden");
    }
}

function getSystemById(systemId) {
    return systemsData.find((system) => Number(system.id) === Number(systemId));
}

function openSystemEditModal(systemId) {
    const system = getSystemById(systemId);
    const modal = document.getElementById("editSystemModal");

    if (!system || !modal) {
        return;
    }

    document.getElementById("editSystemId").value = system.id;
    document.getElementById("editHostname").value = system.hostname || "";
    document.getElementById("editSystemType").value = system.system_type || "PC";
    document.getElementById("editMacAddress").value = system.mac_address || "";
    document.getElementById("editOsVersion").value = system.os_version || system.windows_version || "";
    document.getElementById("editModel").value = system.model || "";
    document.getElementById("editLocation").value = system.location || "";
    document.getElementById("editCurrentUsage").value = system.current_usage || "";
    modal.classList.remove("hidden");
}

function closeSystemEditModal() {
    const modal = document.getElementById("editSystemModal");

    if (modal) {
        modal.classList.add("hidden");
    }
}

async function submitSystemEdit(event) {
    event.preventDefault();

    const systemId = document.getElementById("editSystemId").value;
    const currentSystem = getSystemById(systemId) || {};
    const data = {
        hostname: document.getElementById("editHostname").value,
        system_type: document.getElementById("editSystemType").value,
        mac_address: document.getElementById("editMacAddress").value,
        os_version: document.getElementById("editOsVersion").value,
        model: document.getElementById("editModel").value,
        location: document.getElementById("editLocation").value,
        current_usage: document.getElementById("editCurrentUsage").value,
        inventory_number: currentSystem.inventory_number || "",
        gpu: currentSystem.gpu || "",
        reserved_until: currentSystem.reserved_until || "",
        reinstalled_at: currentSystem.reinstalled_at || "",
        info: currentSystem.info || "",
        helpline: currentSystem.helpline || "",
    };

    try {
        const response = await fetch(`${API_URL}/systems/${systemId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify(data),
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || "System konnte nicht aktualisiert werden");
            return;
        }

        alert(result.message);
        closeSystemEditModal();
        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

function updateCards(systems) {
    const totalSystems = document.getElementById("totalSystems");
    const onlineSystems = document.getElementById("onlineSystems");
    const reservedSystems = document.getElementById("reservedSystems");
    const freeSystems = document.getElementById("freeSystems");

    if (!totalSystems) {
        return;
    }

    totalSystems.innerText = systems.length;
    onlineSystems.innerText = systems.filter((s) => getEffectivePowerStatus(s) === "online").length;
    reservedSystems.innerText = systems.filter((s) => getUsageStatus(s) === "reserved").length;
    freeSystems.innerText = systems.filter((s) => getUsageStatus(s) === "free").length;
}

async function reserveSystem(systemId) {
    const modal = document.getElementById("reservationModal");
    const systemInput = document.getElementById("reservationSystemId");
    const untilInput = document.getElementById("reservationUntil");

    if (!modal || !systemInput || !untilInput) {
        return;
    }

    systemInput.value = systemId;
    untilInput.value = "";
    document.getElementById("reservationPurpose").value = "";
    modal.classList.remove("hidden");
}

function closeReservationModal() {
    const modal = document.getElementById("reservationModal");

    if (modal) {
        modal.classList.add("hidden");
    }
}

async function submitReservation(event) {
    event.preventDefault();

    const systemId = Number(document.getElementById("reservationSystemId").value);
    const until = document.getElementById("reservationUntil").value;
    const purpose = document.getElementById("reservationPurpose").value;

    try {
        const response = await fetch(`${API_URL}/reservations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify({
                system_id: systemId,
                user_id: Number(localStorage.getItem("userId") || "1"),
                reserved_from: new Date().toISOString().slice(0, 19).replace("T", " "),
                reserved_until: until.replace("T", " "),
                purpose,
            }),
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || "Reservierung konnte nicht erstellt werden");
            return;
        }

        alert(result.message);
        closeReservationModal();
        loadSystems();
        loadReservations();
    } catch (error) {
        console.error(error);
    }
}

async function releaseSystem(systemId) {
    try {
        const response = await fetch(`${API_URL}/systems/${systemId}/release`, {
            method: "POST",
            headers: authHeaders(),
        });
        const result = await response.json();
        alert(result.message);
        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

async function togglePower(systemId) {
    try {
        const response = await fetch(`${API_URL}/systems/${systemId}/power`, {
            method: "POST",
            headers: authHeaders(),
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || "Power konnte nicht geändert werden");
            return;
        }

        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

async function addSystem(event) {
    event.preventDefault();

    const data = {
        hostname: document.getElementById("newHostname").value,
        system_type: document.getElementById("newSystemType").value,
        mac_address: document.getElementById("newMacAddress").value,
        os_version: document.getElementById("newOsVersion").value,
        model: document.getElementById("newModel").value,
        location: document.getElementById("newLocation").value,
        inventory_number: "",
    };

    try {
        const response = await fetch(`${API_URL}/systems`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify(data),
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || "System konnte nicht hinzugefügt werden");
            return;
        }

        alert(result.message);
        event.target.reset();
        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

async function deleteSystem(systemId) {
    if (!confirm("Dieses System wirklich löschen?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/systems/${systemId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        const result = await response.json();
        alert(result.message);
        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

function removeFromDashboard(systemId) {
    if (!confirm("Dieses System nur vom Dashboard entfernen? Es bleibt in der Datenbank und auf der Systeme-Seite.")) {
        return;
    }

    if (!hiddenDashboardSystemIds.includes(systemId)) {
        hiddenDashboardSystemIds.push(systemId);
        localStorage.setItem("hiddenDashboardSystemIds", JSON.stringify(hiddenDashboardSystemIds));
    }

    renderSystems(systemsData);
}

async function deleteReservation(reservationId) {
    if (!confirm("Diese Reservierung wirklich löschen?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/reservations/${reservationId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        const result = await response.json();
        alert(result.message);
        loadReservations();
        loadSystems();
    } catch (error) {
        console.error(error);
    }
}

async function deleteUser(userId) {
    if (!confirm("Diesen Benutzer wirklich löschen?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/users/${userId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        const result = await response.json();
        alert(result.message);
        loadUsers();
    } catch (error) {
        console.error(error);
    }
}

function filterSystems() {
    const searchInput = document.getElementById("searchInput");
    const search = searchInput ? normalize(searchInput.value) : "";
    const filtered = systemsData.filter((system) =>
        normalize(system.hostname).includes(search) ||
        normalize(system.system_type).includes(search) ||
        normalize(system.model).includes(search) ||
        normalize(system.location).includes(search) ||
        normalize(system.current_usage).includes(search) ||
        normalize(system.info).includes(search) ||
        normalize(system.helpline).includes(search)
    );

    renderSystems(filtered);
}

applyTheme();
requireLogin();
applyRoleUi();
loadSystems();
loadReservations();
loadUsers();
setInterval(loadSystems, 5000);
