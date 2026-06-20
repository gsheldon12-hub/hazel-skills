# World Cup 2026 → Google Calendar (static ICS)

Get the FIFA World Cup 2026 schedule into Google Calendar by generating a
static `.ics` file from a fixtures CSV and importing it into a **separate**
calendar.

## Why this approach

- **Lowest risk** — an ICS/CSV is just event text/data.
- **No third-party app permissions** — you never grant a calendar app access
  to your Google account.
- **No provider can change events later** — the data is yours.
- **Easy to delete** — just remove the imported calendar.
- **Trade-off:** it will **not** auto-update. If kickoff times, venues, or
  knockout teams change, edit `worldcup.csv`, regenerate, and re-import.

## Files

| File | What it is |
| --- | --- |
| `worldcup.csv` | The fixture list, source of truth. Edit this. |
| `csv_to_ics.py` | Converts the CSV into `worldcup.ics`. |
| `worldcup.ics` | The generated calendar to import (regenerate after edits). |

## 1. Create a separate Google Calendar

Google Calendar → **Settings → Add calendar → Create new calendar** →
name it **World Cup 2026**. Keeping it separate makes it trivial to hide or
delete later.

## 2. (Re)generate the ICS

```bash
cd worldcup-calendar
python3 csv_to_ics.py            # worldcup.csv -> worldcup.ics
# or: python3 csv_to_ics.py myfixtures.csv out.ics
```

Requires Python 3.9+ (uses the standard-library `zoneinfo`). No third-party
packages.

## 3. Import into Google Calendar

Google Calendar (desktop) → **Settings → Import & Export → Import** →
select `worldcup.ics` → choose the **World Cup 2026** calendar → **Import**.

## CSV format

```
Subject,Start Date,Start Time,End Date,End Time,Location,Description,Timezone
USA vs Paraguay,06/12/2026,09:00 PM,,,SoFi Stadium\, Los Angeles,Group D - FIFA World Cup 2026,America/Los_Angeles
```

- `Start Date` / `End Date`: `MM/DD/YYYY`
- `Start Time` / `End Time`: 12-hour, e.g. `09:00 PM`
- `End Date` / `End Time` are optional — blank means **start + 2 hours**.
- `Timezone`: IANA name for the **venue's local time**
  (`America/Los_Angeles`, `America/Mexico_City`, `America/Toronto`, …). This
  matters because the 2026 venues span several time zones, and each kickoff
  is listed in its own venue's local time.

The script handles ICS niceties for you: special-character escaping, CRLF
line endings, and long-line folding.

## Accuracy & verification (read this)

This schedule was reconstructed from web-search results because FIFA's and
Wikipedia's pages were not directly fetchable in the build environment.
Treat it as **best-effort, not authoritative**, and verify before relying on
it:

- **Solid:** the 12 groups and their teams (incl. the March 2026 playoff
  winners), the 16 venues and their time zones, the tournament dates
  (Jun 11 – Jul 19), and the opening match (Estadio Azteca) and final
  (MetLife).
- **Verify against FIFA's official fixtures:**
  - Several group-stage **kickoff times** were derived from reported Eastern
    Time and converted to venue-local; a few may be off by a slot. Known
    soft spots: the Monterrey night games (Matches 12, 36) and a handful of
    Round-of-32/16 times.
  - Group-stage **match numbering / day ordering** and a few **home/away
    orderings** follow FIFA's group-ordered convention; some aggregators
    list them differently.
  - **Knockout teams** are slot labels ("Quarter-final 3", etc.) until the
    bracket fills in.

To correct anything, edit `worldcup.csv` and re-run `python3 csv_to_ics.py`.
The authoritative source is FIFA's official fixtures page
(`fifa.com/.../fifaworldcup/`).

## Safety notes

- CSV/ICS import is low-risk — it is just event data, not code.
- Avoid granting Google-account permissions to third-party calendar apps you
  don't trust.
- Avoid clicking links inside imported calendar events.
- A static import won't auto-update; refresh manually when fixtures change
  (especially knockout-round teams once groups conclude).
