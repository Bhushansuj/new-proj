# Dokumentation zur betrieblichen Projektarbeit

## Entwicklung eines zentralen Systems zur Statusüberwachung von Systemen im NDR-Testcenter

**Prüfungsbewerber:**  
Bhushan Sujwani

**Ausbildungsberuf:**  
Fachinformatiker für Anwendungsentwicklung

**Prüfung:**  
Abschlussprüfung Teil 2 Sommer 2026

**Praktikumsbetrieb:**  
Norddeutscher Rundfunk  
Hugh-Greene-Weg 1  
22529 Hamburg

**Projektbetreuer:**  
Björn Schuster

---

# Inhaltsverzeichnis

1. Einleitung  
2. Projektbeschreibung  
   2.1 Projektumfeld  
   2.2 Projektziel  
   2.3 Projektbegründung  
   2.4 Projektabgrenzung  
3. Projektplanung  
   3.1 Ist-Analyse  
   3.2 Soll-Konzept  
   3.3 Ressourcenplanung  
   3.4 Wirtschaftlichkeitsbetrachtung  
4. Entwurfsphase  
   4.1 Zielplattform und Architektur  
   4.2 Datenbankmodell  
   4.3 Benutzerrollen und Berechtigungskonzept  
   4.4 Benutzeroberfläche  
5. Implementierungsphase  
   5.1 Backend mit FastAPI  
   5.2 MySQL-Datenbank  
   5.3 Frontend mit HTML, CSS und JavaScript  
   5.4 Python-Agent  
   5.5 Import- und Exportfunktionen  
6. Test und Qualitätssicherung  
7. Soll-Ist-Vergleich  
8. Fazit  
9. Anhang

---

# 1. Einleitung

Im Rahmen der Abschlussprüfung Teil 2 für den Ausbildungsberuf Fachinformatiker für Anwendungsentwicklung wurde das Projekt **„Entwicklung eines zentralen Systems zur Statusüberwachung von Systemen im NDR-Testcenter“** durchgeführt.

Ziel des Projektes war die Konzeption und Implementierung einer webbasierten Anwendung, mit der Testsysteme im NDR-Testcenter zentral erfasst, überwacht und verwaltet werden können. Die bisherige Verwaltung erfolgte überwiegend über eine manuell gepflegte Excel-Liste sowie über einzelne technische Prüfungen in bestehenden Systemen. Diese Vorgehensweise führte zu erhöhtem organisatorischem Aufwand, unvollständigen Informationen und einer eingeschränkten Übersicht über die aktuelle Verfügbarkeit der Testressourcen.

Die entwickelte Anwendung stellt eine zentrale Weboberfläche bereit, über die Testsysteme eingesehen, reserviert, bearbeitet und gefiltert werden können. Ergänzend dazu wurde eine REST-API mit FastAPI entwickelt, welche die Kommunikation zwischen Frontend, Datenbank und Python-Agent ermöglicht. Die Daten werden in einer MySQL-Datenbank gespeichert. Zusätzlich wurden Import- und Exportfunktionen umgesetzt, um vorhandene Excel-Daten weiterverwenden und Systemlisten ausgeben zu können.

# 2. Projektbeschreibung

## 2.1 Projektumfeld

Das Projekt wurde im Umfeld des Norddeutschen Rundfunks (NDR) durchgeführt. Der NDR ist die gemeinsame Landesrundfunkanstalt der Bundesländer Hamburg, Mecklenburg-Vorpommern, Niedersachsen und Schleswig-Holstein. Neben redaktionellen und produktionstechnischen Aufgaben betreibt der NDR eine umfangreiche IT-Infrastruktur, die für interne Prozesse, Arbeitsplatzsysteme, Softwaretests und technische Prüfungen genutzt wird.

Das Projekt bezieht sich auf das Testcenter des NDR. Dort werden physische und virtuelle Testsysteme eingesetzt, um Softwareverteilungen, Windows-Versionen, Anwendungen, Konfigurationen und technische Szenarien zu prüfen. Die Testsysteme bestehen unter anderem aus PCs, Laptops und virtuellen Maschinen. Sie werden von unterschiedlichen technischen Mitarbeitern genutzt und müssen daher nachvollziehbar verwaltet werden.

Vor Projektbeginn wurden die relevanten Informationen zu diesen Systemen in einer Excel-Liste gepflegt. Diese Liste enthielt unter anderem Hostname, MAC-Adresse, Betriebssystemversion, Modell, Standort, Verwendungszweck, Reservierungsinformationen und weitere Hinweise.

## 2.2 Projektziel

Das Ziel des Projektes bestand in der Entwicklung eines zentralen webbasierten Systems zur Verwaltung und Statusüberwachung der Testsysteme im NDR-Testcenter.

Die Anwendung sollte folgende Kernfunktionen bereitstellen:

- zentrale Übersicht über alle Testsysteme
- Anzeige von Hostname, MAC-Adresse, Betriebssystem, Modell und Standort
- Anzeige des Power- und Nutzungsstatus
- Reservierung von Systemen durch berechtigte Benutzer
- Rollenmodell mit Administratoren und Mitarbeitern
- Bearbeitung von Systemdaten durch Administratoren
- Import vorhandener Excel-Daten
- Export der Systemliste als CSV-Datei
- Statusübermittlung durch einen Python-Agenten
- Filtermöglichkeiten im Dashboard

Durch diese Funktionen soll die bisherige manuelle Verwaltung übersichtlicher, aktueller und weniger fehleranfällig werden.

## 2.3 Projektbegründung

Die bisherige Arbeitsweise im Testcenter basierte stark auf manueller Pflege und manueller Kontrolle. Die Excel-Liste stellte zwar viele benötigte Informationen bereit, musste jedoch von Hand aktualisiert werden. Dadurch konnten veraltete oder unvollständige Daten entstehen. Außerdem war nicht immer sofort ersichtlich, ob ein System aktuell verfügbar, reserviert, online oder offline war.

Für Techniker bedeutete dies zusätzlichen Aufwand, da der Systemstatus teilweise über verschiedene Quellen geprüft werden musste. Beispielsweise mussten Informationen aus der Excel-Liste, aus bestehenden Verwaltungssystemen oder direkt aus dem Testcenter zusammengeführt werden.

Die neue Anwendung reduziert diesen Aufwand, indem sie eine zentrale Datenbasis schafft und wichtige Informationen in einer Weboberfläche bündelt. Dadurch können freie Systeme schneller gefunden, Reservierungen nachvollziehbarer verwaltet und Statusinformationen übersichtlicher dargestellt werden.

## 2.4 Projektabgrenzung

Der Fokus des Projektes liegt auf der Entwicklung eines Prototyps bzw. einer funktionsfähigen Anwendung für das Testcenter. Bestandteil des Projektes sind:

- Entwicklung der Weboberfläche
- Entwicklung der REST-API
- Anbindung einer MySQL-Datenbank
- Umsetzung eines einfachen Rollen- und Login-Konzeptes
- Implementierung von Reservierungsfunktionen
- Import vorhandener Excel-Daten
- Export der Systemübersicht als CSV-Datei
- Entwicklung eines Python-Agenten zur Statusübermittlung

Nicht Bestandteil des Projektes ist eine vollständige unternehmensweite Einführung, eine direkte Integration in Active Directory, MECM oder andere zentrale NDR-Systeme sowie ein produktiver Betrieb mit vollständigem Sicherheits- und Berechtigungskonzept. Diese Punkte können als mögliche Erweiterungen betrachtet werden.

# 3. Projektplanung

## 3.1 Ist-Analyse

Die Ist-Analyse bildet die Grundlage für die Entwicklung der neuen Anwendung. Dabei wurden sowohl die vorhandene technische Umgebung als auch der bisherige organisatorische Ablauf im NDR-Testcenter betrachtet. Ziel dieser Analyse war es, die Schwachstellen der bestehenden Arbeitsweise zu erkennen und daraus Anforderungen für das neue System abzuleiten.

### 3.1.1 Analyse der bestehenden IT-Infrastruktur

Das NDR-Testcenter verfügt über verschiedene physische und virtuelle Testsysteme. Dazu gehören PCs, Laptops und virtuelle Maschinen, die für Softwaretests, Windows-Tests, Paketierung, Anwendungsvalidierung und weitere technische Prüfungen verwendet werden.

Die Systeme basieren überwiegend auf Windows-Betriebssystemen. Ein Teil der Testumgebung besteht aus virtuellen Maschinen, die über Hyper-V betrieben werden. Die Verwaltung und technische Kontrolle der Systeme erfolgt teilweise über bestehende Werkzeuge wie MECM sowie über manuelle Dokumentation.

Für die Projektdurchführung standen eine lokale Entwicklungsumgebung mit Windows, XAMPP, MySQL, phpMyAdmin, Python und einem Webbrowser zur Verfügung. Die Anwendung wurde als Webanwendung umgesetzt, sodass keine zusätzliche Client-Installation für die Benutzeroberfläche erforderlich ist. Der Zugriff erfolgt über den Browser, während die Daten zentral in einer MySQL-Datenbank gespeichert werden.

### 3.1.2 Analyse des gegenwärtigen Geschäftsprozesses

Im bisherigen Prozess werden die Testsysteme des NDR-Testcenters hauptsächlich über eine Excel-Liste dokumentiert. Diese Liste enthält wichtige Stammdaten und organisatorische Informationen zu den einzelnen Systemen, beispielsweise Hostname, MAC-Adresse, Betriebssystemversion, Modell, Standort, Verwendung, Reservierungsende und weitere Hinweise.

Wenn ein Techniker ein Testsystem benötigt, muss zunächst geprüft werden, welches System verfügbar ist. Dafür wird die Excel-Liste herangezogen oder der Zustand des Systems direkt im Testcenter bzw. über bestehende Verwaltungssysteme kontrolliert. Reservierungen oder Verwendungszwecke werden ebenfalls manuell in der Liste gepflegt.

Dieser Ablauf ist grundsätzlich verständlich und einfach, erfordert jedoch eine regelmäßige manuelle Aktualisierung. Dadurch hängt die Qualität der Informationen stark davon ab, ob Änderungen zeitnah und korrekt eingetragen werden. Eine zentrale Weboberfläche, die den aktuellen Status übersichtlich darstellt und Reservierungen systemgeführt verwaltet, existierte bisher nicht.

### 3.1.3 Identifizierte Schwachstellen und Defizite

Bei der Analyse des bestehenden Prozesses wurden mehrere Schwachstellen festgestellt:

- Die Excel-Liste muss manuell gepflegt werden.
- Änderungen an Standort, Verwendung oder Reservierungsstatus können veraltet sein.
- Der Power-Status eines Systems ist nicht direkt aus der Liste ersichtlich.
- Reservierungen sind nicht systemgeführt und dadurch weniger nachvollziehbar.
- Es gibt kein Rollenmodell für Administratoren und Mitarbeiter.
- Mehrere Benutzer können mit unterschiedlichen Informationsständen arbeiten.
- Eine automatische Zusammenführung von Stammdaten und Statusinformationen existiert nicht.
- Der Export und die Weiterverarbeitung der Daten sind nur eingeschränkt strukturiert möglich.

Diese Schwachstellen führen zu zusätzlichem Abstimmungsaufwand im Testcenter. Techniker müssen Informationen teilweise aus mehreren Quellen zusammensuchen oder manuell überprüfen. Daraus ergibt sich der Bedarf an einer zentralen Anwendung, welche die vorhandenen Daten strukturiert speichert, übersichtlich darstellt und wichtige Prozesse wie Reservierung, Statusprüfung und Export unterstützt.

## 3.2 Soll-Konzept

Im Soll-Zustand soll eine zentrale Webanwendung die Verwaltung und Statusüberwachung der Testsysteme unterstützen. Die Anwendung soll die bisherige Excel-Liste nicht vollständig ersetzen, aber die manuelle Arbeitsweise deutlich verbessern und perspektivisch als zentrale Informationsquelle dienen.

### 3.2.1 Zielsetzung ausarbeiten

Das Ziel des Projektes besteht darin, eine webbasierte Anwendung bereitzustellen, mit der die Testsysteme des NDR-Testcenters zentral eingesehen, verwaltet und reserviert werden können. Die Anwendung soll den Technikern eine schnelle Übersicht über verfügbare Systeme ermöglichen und den manuellen Pflegeaufwand reduzieren.

Die wichtigsten fachlichen Ziele sind:

- zentrale Darstellung aller Testsysteme
- Anzeige von Stammdaten wie Hostname, MAC-Adresse, Betriebssystem, Modell und Standort
- Anzeige des aktuellen Power- und Nutzungsstatus
- Reservierung von Systemen über eine Weboberfläche
- rollenbasierter Zugriff für Administratoren und Mitarbeiter
- Bearbeitung von Systemdaten durch Administratoren
- Import vorhandener Excel-Daten
- Export der Systemübersicht als CSV-Datei
- Anzeige des letzten Agent-Kontaktes
- Möglichkeit zur manuellen Statusprüfung

Für Mitarbeiter soll der Fokus auf dem Einsehen und Reservieren von Systemen liegen. Administratoren erhalten zusätzliche Funktionen, beispielsweise zur Benutzerverwaltung, Bearbeitung von Systemdaten und Löschung von Datensätzen.

### 3.2.2 Modellierung der neuen Datenbankstruktur

Für die zentrale Speicherung der Daten wurde eine relationale MySQL-Datenbank vorgesehen. Die Datenbankstruktur wurde so modelliert, dass Stammdaten, Statusinformationen, Reservierungen und Benutzerinformationen getrennt, aber logisch miteinander verbunden gespeichert werden können.

Die wichtigsten Tabellen sind:

| Tabelle | Beschreibung |
|---|---|
| roles | Speicherung der Benutzerrollen |
| users | Speicherung der Benutzerkonten und Zuordnung zu Rollen |
| systems | Speicherung der Stammdaten der Testsysteme |
| system_status | Speicherung dynamischer Statusinformationen |
| reservations | Speicherung der Reservierungen |

Die Tabelle `systems` bildet die zentrale Stammdatentabelle. Sie enthält Informationen wie Hostname, MAC-Adresse, Modell, Standort, Betriebssystemversion, Verwendung und Hinweise. Die Tabelle `system_status` speichert veränderliche Informationen wie Power-Status, Nutzungsstatus, Windows-Version, letzter Benutzer und letzter Agent-Kontakt. Dadurch werden statische und dynamische Daten voneinander getrennt.

Reservierungen werden in der Tabelle `reservations` gespeichert. Diese enthält unter anderem das reservierte System, den Benutzer, den Zeitraum und den Zweck der Reservierung. Durch diese Trennung kann nachvollzogen werden, welches System zu welchem Zeitpunkt und für welchen Zweck reserviert wurde.

Die Benutzerverwaltung besteht aus den Tabellen `users` und `roles`. Dadurch kann zwischen Administratoren und Mitarbeitern unterschieden werden. Die Rollen bilden die Grundlage für das Berechtigungskonzept in der Anwendung.

### 3.2.3 Beschreibung der benötigten Komponenten: Datenbank, Programmiersprache, Systeme und Software / Ressourcenplanung

Für die Umsetzung des Soll-Konzeptes wurden verschiedene technische Komponenten benötigt. Diese Komponenten wurden so ausgewählt, dass sie für eine lokale Entwicklungsumgebung geeignet sind und gleichzeitig die Anforderungen des Projektes erfüllen.

| Komponente | Verwendung |
|---|---|
| MySQL | Speicherung der Systeme, Reservierungen, Benutzer und Statusdaten |
| FastAPI | Entwicklung der REST-API |
| Python | Backend, Agent und Excel-Importskript |
| HTML | Struktur der Weboberfläche |
| CSS | Gestaltung der Benutzeroberfläche inklusive Dark-Mode |
| JavaScript | Dynamische Funktionen im Frontend und API-Kommunikation |
| XAMPP | Lokale Web- und Datenbankumgebung |
| phpMyAdmin | Verwaltung und Kontrolle der MySQL-Datenbank |
| Browser | Bedienung und Test der Weboberfläche |
| Excel-Datei | Ausgangsdatenbestand des NDR-Testcenters |

Die Anwendung wurde lokal entwickelt und getestet. Das Frontend wird im Browser ausgeführt und kommuniziert über HTTP mit dem FastAPI-Backend. Das Backend verarbeitet die Anfragen und greift auf die MySQL-Datenbank zu. Der Python-Agent kann Statusinformationen an die API senden. Zusätzlich wurde ein Importskript umgesetzt, mit dem die vorhandene Excel-Liste in die Datenbank übernommen werden kann.

Durch diese Aufteilung entsteht eine klare Struktur aus Benutzeroberfläche, Geschäftslogik und Datenhaltung. Gleichzeitig bleibt das System erweiterbar, da weitere Schnittstellen oder zusätzliche Funktionen später ergänzt werden können.

## 3.3 Ressourcenplanung

Für die Umsetzung wurden folgende Ressourcen verwendet:

| Ressource | Verwendung |
|---|---|
| Windows-Arbeitsplatz | Entwicklung und Test |
| XAMPP / MySQL | Lokale Datenbankumgebung |
| FastAPI | Backend-Framework |
| Python | Backend, Agent und Importskript |
| HTML, CSS, JavaScript | Weboberfläche |
| phpMyAdmin | Datenbankverwaltung |
| Visual Studio Code / Editor | Quellcodebearbeitung |
| Browser | Funktionstests der Weboberfläche |

## 3.4 Wirtschaftlichkeitsbetrachtung

Die Entwicklung einer eigenen Anwendung wurde gegenüber der Nutzung einer Standardsoftware bevorzugt, da die Anforderungen des NDR-Testcenters sehr spezifisch sind. Allgemeine Monitoring- oder Inventarisierungslösungen bieten zwar viele technische Funktionen, bilden jedoch nicht ohne Weiteres die Kombination aus Testsystemverwaltung, Reservierung, Excel-Datenübernahme und rollenbasierter Weboberfläche ab.

Eine Eigenentwicklung bietet daher folgende Vorteile:

- gezielte Anpassung an die vorhandene Excel-Struktur
- geringe Lizenzkosten
- flexible Erweiterbarkeit
- bessere Integration in den konkreten Arbeitsablauf des Testcenters
- klare Abgrenzung des Funktionsumfangs für das Abschlussprojekt

# 4. Entwurfsphase

## 4.1 Zielplattform und Architektur

Die Anwendung wurde als klassische Webanwendung mit getrenntem Frontend und Backend konzipiert. Das Frontend kommuniziert über HTTP-Anfragen mit der REST-API. Die API verarbeitet die Anfragen und speichert bzw. liest Daten aus der MySQL-Datenbank.

Die Architektur lässt sich wie folgt beschreiben:

```text
Browser / Frontend
        |
        | HTTP / REST
        v
FastAPI Backend
        |
        | SQL
        v
MySQL-Datenbank
        ^
        |
Python-Agent
```

## 4.2 Datenbankmodell

Die Datenbank besteht aus mehreren Tabellen, welche die wichtigsten fachlichen Bereiche abbilden:

| Tabelle | Zweck |
|---|---|
| roles | Speicherung der Benutzerrollen |
| users | Speicherung der Benutzerkonten |
| systems | Stammdaten der Testsysteme |
| system_status | aktuelle Statusinformationen |
| reservations | Reservierungen der Systeme |

Die Tabelle `systems` enthält die Stammdaten der Systeme. Die Tabelle `system_status` speichert dynamische Informationen wie Power-Status, Nutzungsstatus, letzte Anmeldung und letzten Agent-Kontakt. Reservierungen werden separat in der Tabelle `reservations` gespeichert.

## 4.3 Benutzerrollen und Berechtigungskonzept

Es wurden zwei Rollen umgesetzt:

| Rolle | Berechtigungen |
|---|---|
| admin | Zugriff auf Dashboard, Systeme, Reservierungen, Benutzerverwaltung, Bearbeiten und Löschen |
| mitarbeiter | Zugriff auf Systeme und Reservierungen, Reservieren von Systemen |

Der Zugriff erfolgt über eine Login-Funktion. Nach erfolgreicher Anmeldung erhält der Benutzer ein Token. Dieses Token wird bei geschützten API-Anfragen verwendet.

## 4.4 Benutzeroberfläche

Die Weboberfläche besteht aus mehreren Bereichen:

- Dashboard mit Kennzahlen und Filterfunktionen
- Systemübersicht mit kompakter Tabelle und Detailansicht
- Reservierungsübersicht
- Benutzerverwaltung
- Login-Seite

Zusätzlich wurde ein Dark-Mode integriert, der die Bedienbarkeit verbessert und als moderne Darstellungsoption dient.

# 5. Implementierungsphase

## 5.1 Backend mit FastAPI

Das Backend wurde mit FastAPI umgesetzt. Es stellt REST-Endpunkte für Login, Systeme, Reservierungen, Benutzerverwaltung und Agent-Status bereit.

Wichtige Endpunkte sind:

| Methode | Route | Zweck |
|---|---|---|
| POST | /login | Anmeldung |
| GET | /systems | Systeme abrufen |
| POST | /systems | System anlegen |
| PUT | /systems/{id} | System bearbeiten |
| DELETE | /systems/{id} | System löschen |
| POST | /reservations | Reservierung erstellen |
| GET | /reservations | Reservierungen abrufen |
| POST | /agent/status | Agent-Status empfangen |

## 5.2 MySQL-Datenbank

Die Daten werden in einer MySQL-Datenbank gespeichert. Die Verbindung wird über Umgebungsvariablen in der Datei `.env` konfiguriert. Dadurch können Zugangsdaten getrennt vom Quellcode gepflegt werden.

## 5.3 Frontend mit HTML, CSS und JavaScript

Das Frontend wurde mit HTML, CSS und JavaScript umgesetzt. Die Seiten greifen über `fetch` auf die REST-API zu. Die Systemdaten werden dynamisch geladen und in Tabellen dargestellt.

Zu den umgesetzten Funktionen gehören:

- Login und Logout
- rollenabhängige Navigation
- Dashboard-Kennzahlen
- Filter nach Status
- Reservierungsdialog mit Datum/Uhrzeit
- Bearbeitungsdialog für Systemdaten
- CSV-Export
- Dark-/Light-Mode

## 5.4 Python-Agent

Der Python-Agent sammelt lokale Systeminformationen und sendet diese an die API. Dazu gehören unter anderem:

- Hostname
- Power-Status
- Windows-Version
- letzter Benutzer
- Zeitstempel

Der Agent nutzt einen API-Token, damit nicht beliebige Clients Statusdaten senden können.

## 5.5 Import- und Exportfunktionen

Für die Übernahme der bestehenden Excel-Liste wurde ein Python-Importskript umgesetzt. Dieses liest die Excel-Datei aus und speichert die Systeme in der Datenbank.

Zusätzlich kann die Weboberfläche die aktuelle Systemliste als CSV-Datei exportieren. Diese Datei kann in Excel geöffnet und weiterverarbeitet werden.

# 6. Test und Qualitätssicherung

Die Anwendung wurde funktional über den Browser und über direkte API-Aufrufe getestet. Wichtige Testfälle waren:

| Testfall | Erwartetes Ergebnis | Status |
|---|---|---|
| Login als admin | Zugriff auf alle Bereiche | erfolgreich |
| Login als mitarbeiter | Zugriff auf Systeme und Reservierungen | erfolgreich |
| System reservieren | System wird reserviert und erscheint in Reservierungen | erfolgreich |
| Reservierung löschen | System wird wieder frei, wenn keine Reservierung mehr besteht | erfolgreich |
| System bearbeiten | geänderte Daten erscheinen in der Übersicht | erfolgreich |
| CSV exportieren | CSV-Datei wird heruntergeladen | erfolgreich |
| Power-Status ändern | Status wechselt zwischen online und offline | erfolgreich |
| Excel importieren | Systeme werden aus Excel übernommen | erfolgreich |

# 7. Soll-Ist-Vergleich

| Anforderung | Umsetzung |
|---|---|
| zentrale Weboberfläche | umgesetzt |
| Systemübersicht | umgesetzt |
| Reservierungsfunktion | umgesetzt |
| Rollenmodell | umgesetzt |
| MySQL-Datenbank | umgesetzt |
| REST-API | umgesetzt |
| Python-Agent | umgesetzt |
| Excel-Import | umgesetzt |
| CSV-Export | umgesetzt |
| Dark-Mode | zusätzlich umgesetzt |

Die im Projektantrag definierten Kernanforderungen wurden erfüllt. Zusätzlich wurden einige Komfortfunktionen ergänzt, beispielsweise Dark-Mode, Dashboard-Filter und CSV-Export.

# 8. Fazit

Mit dem Projekt wurde eine zentrale Anwendung zur Verwaltung und Statusüberwachung der Testsysteme im NDR-Testcenter umgesetzt. Die Anwendung verbessert die Übersicht über vorhandene Systeme, Reservierungen und Statusinformationen. Im Vergleich zur rein manuellen Excel-Verwaltung bietet die Lösung eine strukturiertere Datenhaltung und eine bessere Benutzerführung.

Die Umsetzung zeigt, wie eine bestehende manuelle Arbeitsweise durch eine webbasierte Anwendung ergänzt und teilweise automatisiert werden kann. Besonders hilfreich sind die rollenbasierte Anmeldung, die Reservierungsfunktion sowie die Möglichkeit, vorhandene Excel-Daten zu importieren und Systemdaten als CSV zu exportieren.

Mögliche Erweiterungen wären eine produktive Anbindung an zentrale NDR-Systeme, eine erweiterte Rechteverwaltung, automatisierte Hintergrundjobs für Statusprüfungen sowie eine vollständige Integration in bestehende Inventarisierungs- oder Monitoring-Systeme.

# 9. Anhang

Mögliche Anhänge:

- Screenshots der Excel-Ausgangsliste
- Screenshots der Weboberfläche
- ER-Diagramm
- API-Beispiele
- SQL-Schema
- Testprotokoll
- Quellcodeauszüge
