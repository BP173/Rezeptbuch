# Rezeptbuch

Kleine **Flask**-Web-App zum Sammeln von Rezepten: Übersicht mit Karten-Vorschau, Detailansicht mit skalierbaren Portionen, radiales **A–Z-Rad** für den ersten Buchstaben des Titels, Volltextsuche im Titel und **Admin-Session** zum Bearbeiten. Optional gibt es **`POST /api/add`** mit API-Key für Automation (z. B. n8n).

## Funktionen

- **Radiales Buchstabenrad** zum Filtern nach Anfangsbuchstabe (inkl. Tastaturbedienung, Touch-optimiert).
- **Suche** und **Alle Rezepte** in der Übersicht.
- **Karten** mit Kurzbeschreibung und Zutaten-Vorschau; Klick öffnet die Detailansicht.
- **Portionen skalieren** in der Detailansicht (Zutatenmengen relativ zur Basis-Portion).
- **Admin**: Anmeldung per Passwort (Session), dann Rezepte **anlegen**, **bearbeiten** und **löschen**.
- **API**: `POST /api/add` mit `X-API-Key` (oder `Authorization: Bearer …`) zum Anlegen ohne Browser-Login.
- **Mobile**: Bottom-Navigation und Abstände für **Safe Area** (z. B. iPhone-Home-Indikator).

## Technik

- Python 3, **Flask**, **Flask-SQLAlchemy**
- Standardmäßig **SQLite** (`recipes.db` lokal oder per `DATABASE_URL`)

## Installation (lokal)

1. Repository klonen und ins Verzeichnis wechseln:

   ```sh
   git clone https://github.com/BP173/Rezeptbuch.git
   cd Rezeptbuch
   ```

2. Abhängigkeiten installieren:

   ```sh
   pip install -r requirements.txt
   ```

3. Optional `.env` aus Vorlage anlegen und Werte setzen (siehe unten).

4. App starten:

   ```sh
   python app.py
   ```

   Im Browser die ausgegebene URL öffnen (Standard: `http://127.0.0.1:5000`).

## Umgebungsvariablen

| Variable | Bedeutung |
|----------|-----------|
| `SECRET_KEY` | Flask-Session signieren; in Produktion **setzen**. |
| `ADMIN_PASSWORD` | Passwort für Admin-Login in der UI. |
| `API_ADD_KEY` | Geheimer Schlüssel für `POST /api/add`. Leer lassen, wenn die Route nicht genutzt werden soll (liefert dann 503). |
| `DATABASE_URL` | SQLAlchemy-URI, z. B. `sqlite:///recipes.db` oder `sqlite:////data/recipes.db` im Container. |

Siehe auch `.env.example`.

## API-Kurzüberblick

| Methode | Pfad | Auth | Zweck |
|---------|------|------|--------|
| `GET` | `/` | — | Web-Oberfläche |
| `GET` | `/recipes`, `/recipes/<Buchstabe>`, `/search?query=…`, `/recipe/<id>` | — | JSON lesen |
| `POST` | `/admin/login`, `POST` `/admin/logout`, `GET` `/admin/status` | — | Admin-Session |
| `POST` | `/add` | Session (Admin) | Rezept anlegen |
| `PUT` | `/update/<id>` | Session (Admin) | Rezept aktualisieren |
| `DELETE` | `/delete/<id>` | Session (Admin) | Rezept löschen |
| `POST` | `/api/add` | Header `X-API-Key: <API_ADD_KEY>` | Rezept per JSON anlegen |

**JSON für Anlegen/Aktualisieren** (vereinfacht): `title`, optional `description`, optional `servings`, `ingredients` als **Array** von Objekten mit `name`, `amount`, `unit`.

## Docker

Image baut die App und startet **Gunicorn** mit **`wsgi:app`** (ein Worker, sinnvoll mit SQLite).

```sh
cp .env.example .env
# .env bearbeiten (SECRET_KEY, ADMIN_PASSWORD, ggf. API_ADD_KEY)
docker compose up -d --build
```

Die Compose-Datei bindet ein Volume unter `/data` für die Datenbank-Datei, wenn `DATABASE_URL` darauf zeigt (siehe `.env.example`).

## Sicherheitshinweise

- `SECRET_KEY` und `ADMIN_PASSWORD` für echte Deployments **immer** setzen.
- `API_ADD_KEY` nur setzen, wenn Automation benötigt wird; Schlüssel wie ein Passwort behandeln.
