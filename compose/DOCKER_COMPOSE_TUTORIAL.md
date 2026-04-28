# Docker Compose Tutorial - Zusammenfassung

## 1. Diagramm der Container-Architektur

```
┌─────────────────────────────────────────────────────┐
│         Docker Compose Application                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐        ┌──────────────────┐  │
│  │   Web Service    │        │  Redis Service   │  │
│  │  (Flask App)     │        │  (Cache/Database)│  │
│  │                  │        │                  │  │
│  │  Python 3.12     │        │  redis:alpine    │  │
│  │  - Flask         │◄──────►│  Port 6379       │  │
│  │  - Redis Client  │        │  Volume: /data   │  │
│  │  Port 5000       │        │  (Persistence)   │  │
│  │  (internal)      │        │                  │  │
│  └──────┬───────────┘        └──────────────────┘  │
│         │                                           │
│    Port Mapping                                     │
│    8000:5000                                        │
│         │                                           │
└─────────┼───────────────────────────────────────────┘
          │
      ┌───▼────┐
      │ Host   │
      │ Port   │
      │ 8000   │
      └────────┘
```

---

## 2. Beschreibung der Container

### Web Service (Flask Application)
- **Image**: Python 3.12 Alpine (benutzerdefiniertes Image aus Dockerfile)
- **Funktion**: Flask-Webserver für die Python-Anwendung
- **Port**: 5000 (intern) → 8000 (Host)
- **Abhängigkeiten**: Wartet auf Redis Health Check
- **Watch-Funktion**: Automatische Code-Synchronisation bei Änderungen
- **Umgebungsvariablen**: 
  - `REDIS_HOST=redis` (Service-Name als Hostname)
  - `REDIS_PORT=6379`

### Redis Service
- **Image**: `redis:alpine` (offizielles Redis Image)
- **Funktion**: In-Memory Datenbank/Cache für Visit-Counter
- **Port**: 6379 (Standard Redis Port)
- **Persistenz**: Named Volume `redis-data:/data` speichert Daten auf dem Host
- **Health Check**: `redis-cli ping` prüft alle 5 Sekunden ob Redis läuft
- **Netzwerk**: Gehört zum gleichen Docker Network wie Web Service

---

## 3. Beantwortung der Fragen

### Was ist Redis?

Redis ist eine **Open-Source in-Memory Datenbank und Cache**:

- **Hauptmerkmale**:
  - Speichert Daten im Arbeitsspeicher (sehr schnell)
  - Unterstützt verschiedene Datentypen (Strings, Lists, Sets, Hashes, Sorted Sets)
  - Persistenz optional (RDB snapshots, AOF logs)
  - Client-Server Architektur über TCP/IP

- **Anwendungsfälle** (im Tutorial):
  - Speichern des Visit-Counters (Hits)
  - Session Management
  - Caching häufig abgerufener Daten
  - Message Queuing

- **Im Tutorial**: Redis speichert den "Hits"-Counter und erhöht ihn bei jedem Besuch der Webseite

---

### Welche Ports werden genutzt?

| Service | Interner Port | Host Port | Protokoll | Verwendung |
|---------|---------------|-----------|-----------|-----------|
| Web (Flask) | 5000 | 8000 | HTTP | Webserver |
| Redis | 6379 | - | TCP | Datenbank (nur intern) |

**Besonderheiten**:
- Redis Port 6379 ist **nicht extern gemappt** - nur der Web-Container kann darauf zugreifen
- Die Kommunikation erfolgt über das interne Docker Network
- Der Service-Name `redis` funktioniert als Hostname innerhalb des Networks

---

### Was ist die Bedeutung von ENV im Dockerfile?

`ENV` ist ein Dockerfile-Befehl zur **Deklaration von Umgebungsvariablen**:

```dockerfile
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
```

**Funktionsweise**:
- Setzt Umgebungsvariablen in der Image-Definition
- Diese Variablen sind verfügbar in allen Prozessen im Container
- Flask nutzt diese für die Konfiguration der Anwendung

**Unterschied ENV vs. docker-compose.yml `environment`**:

| Ort | Zweck | Beispiel |
|-----|-------|---------|
| **Dockerfile ENV** | Image-Ebene, während Build | FLASK_APP=app.py (Teil des Images) |
| **compose.yaml environment** | Runtime-Ebene, beim Start | REDIS_HOST=redis (nur für Container zur Laufzeit) |

**Beispiel aus Tutorial**:
```dockerfile
ENV FLASK_APP=app.py        # Flask weiß welche App zu starten ist
ENV FLASK_RUN_HOST=0.0.0.0  # Flask lauscht auf allen Interfaces
```

```yaml
environment:               # Erst zur Laufzeit gesetzt
  - REDIS_HOST=redis      # App kann Redis finden
  - REDIS_PORT=6379       # App kennt den Redis Port
```

---

## 4. Besonderheiten von Docker Compose

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s      # Test alle 5 Sekunden
  timeout: 3s       # Max 3 Sekunden warten
  retries: 5        # 5x fehlgeschlagen = unhealthy
  start_period: 10s # 10s Wartezeit vor erstem Test
```

### Service Dependencies
```yaml
depends_on:
  redis:
    condition: service_healthy  # Warte bis Redis healthy ist
```

### Volumes (Persistenz)
```yaml
volumes:
  redis-data:/data  # Named Volume montiert bei /data im Container
volumes:
  redis-data:       # Top-level Definition registriert Volume
```

### Watch (Live-Entwicklung)
```yaml
develop:
  watch:
    - action: sync+restart      # Datei-Änderungen synchro
      path: .
      target: /code
    - action: rebuild           # requirements.txt neu bauen
      path: requirements.txt
```

---

## 5. Workflow beim Start

```
docker compose up
    ↓
1. Image für Web bauen (aus Dockerfile)
2. Redis Image pullen (redis:alpine)
3. Named Volume erstellen (redis-data)
4. Network erstellen (intern)
5. Redis Container starten
6. Health Check laufen lassen (max 25 Sekunden)
7. Wenn Redis healthy: Web Container starten
8. Flask App startet und verbindet sich mit Redis
9. Anwendung läuft auf http://localhost:8000
```

---

## 6. Befehle zum Debuggen

```bash
# Konfiguration anschauen (mit substituierten Variablen)
docker compose config

# Live-Logs aller Services
docker compose logs -f

# Logs nur eines Services
docker compose logs -f web

# Befehl im laufenden Container ausführen
docker compose exec web env | grep REDIS

# Redis-Daten prüfen
docker compose exec redis redis-cli GET hits

# Container stoppen und starten
docker compose down
docker compose up -d

# Alles löschen inklusive Volumes
docker compose down -v
```

---

## Zusammenfassung

Docker Compose vereinfacht die Verwaltung mehrerer Container durch:
- **Deklarative YAML-Konfiguration** statt manueller Docker-Befehle
- **Automatische Netzwerk-Erstellung** für Service-Kommunikation
- **Health Checks** für sichere Start-Reihenfolge
- **Named Volumes** für Datenpersistenz
- **Environment Variables** für flexible Konfiguration
- **Watch-Modus** für schnellere Entwicklung
