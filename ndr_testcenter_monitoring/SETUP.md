# NDR Testcenter Monitoring

## Backend starten

```powershell
cd C:\xampp\htdocs\final_projekt\new-proj\ndr_testcenter_monitoring
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```

## Datenbank erweitern

Die Datei `database/schema_update.sql` erweitert die Tabelle `systems` um die Felder aus der NDR-Excel-Liste:

- OS
- GPU
- Verwendung
- Reserviert bis
- Neu aufgesetzt am
- Info
- Helpline

Die SQL-Datei muss einmal in phpMyAdmin oder direkt in MariaDB/MySQL ausgeführt werden.

## Agent starten

```powershell
cd C:\xampp\htdocs\final_projekt\new-proj\ndr_testcenter_monitoring\agent
$env:NDR_AGENT_TOKEN="ndr-agent-token"
python agent.py
```

Der gleiche Token muss im Backend als `AGENT_API_TOKEN` gesetzt sein.

## Excel-Liste importieren

```powershell
cd C:\xampp\htdocs\final_projekt\new-proj\ndr_testcenter_monitoring
pip install -r requirements.txt
python scripts\import_excel.py "C:\Users\Testcenter\Downloads\Testcenter Clients 1.xlsx"
```

Der Import nutzt die Datenbankverbindung aus `backend\.env` und aktualisiert vorhandene Systeme anhand des Hostnamens.
