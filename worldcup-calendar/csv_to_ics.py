#!/usr/bin/env python3
"""Convert a World Cup fixtures CSV into a static ICS calendar file.

Why static ICS:
  - Lowest risk: it is just event text/data, no third-party app permissions.
  - No calendar provider can change events later.
  - Easy to delete: remove the imported calendar.
  - Trade-off: it will NOT auto-update if kickoff times, venues, or knockout
    teams change. Re-run this script and re-import to refresh.

CSV format (header required):
  Subject,Start Date,Start Time,End Date,End Time,Location,Description,Timezone

  - Start/End Date: MM/DD/YYYY
  - Start/End Time: 12-hour, e.g. "09:00 PM"
  - End Date/End Time are optional; if blank, the end defaults to start + 2h.
  - Timezone: an IANA name for the *venue's* local time (e.g.
    "America/Los_Angeles"). Optional; defaults to DEFAULT_TZ below. This
    matters for World Cup 2026 because venues span several US/Canada/Mexico
    time zones, and each kickoff time is given in its own venue's local time.

Usage:
  python3 csv_to_ics.py [input.csv] [output.ics]
  (defaults: worldcup.csv -> worldcup.ics)
"""

import csv
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

DEFAULT_INPUT = "worldcup.csv"
DEFAULT_OUTPUT = "worldcup.ics"
DEFAULT_TZ = "America/New_York"
DEFAULT_DURATION = timedelta(hours=2)


def parse_dt(date_str, time_str, tz):
    """Parse 'MM/DD/YYYY' + 'HH:MM AM/PM' into a tz-aware datetime."""
    naive = datetime.strptime(f"{date_str.strip()} {time_str.strip()}", "%m/%d/%Y %I:%M %p")
    return naive.replace(tzinfo=ZoneInfo(tz))


def fmt_local(dt):
    """Format a local datetime for use with DTSTART;TZID=...:"""
    return dt.strftime("%Y%m%dT%H%M%S")


def fmt_utc(dt):
    """Format a datetime as a UTC timestamp (for DTSTAMP)."""
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def escape(text):
    """Escape special characters in ICS TEXT values (RFC 5545 sec 3.3.11)."""
    if text is None:
        return ""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def fold(line):
    """Fold lines longer than 75 octets per RFC 5545 (continuation = space)."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    pieces = []
    while len(encoded) > 75:
        # Find a split point that doesn't break a multibyte char.
        cut = 75
        while cut > 0 and (encoded[cut] & 0xC0) == 0x80:
            cut -= 1
        pieces.append(encoded[:cut].decode("utf-8"))
        encoded = encoded[cut:]
    pieces.append(encoded.decode("utf-8"))
    return "\r\n ".join(pieces)


def build_event(row):
    tz = (row.get("Timezone") or "").strip() or DEFAULT_TZ
    start = parse_dt(row["Start Date"], row["Start Time"], tz)

    end_date = (row.get("End Date") or "").strip()
    end_time = (row.get("End Time") or "").strip()
    if end_date and end_time:
        end = parse_dt(end_date, end_time, tz)
    else:
        end = start + DEFAULT_DURATION

    now = datetime.now(timezone.utc)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uuid4()}@worldcup-local",
        f"DTSTAMP:{fmt_utc(now)}",
        f"DTSTART;TZID={tz}:{fmt_local(start)}",
        f"DTEND;TZID={tz}:{fmt_local(end)}",
        f"SUMMARY:{escape(row['Subject'])}",
        f"LOCATION:{escape(row.get('Location', ''))}",
        f"DESCRIPTION:{escape(row.get('Description', ''))}",
        "END:VEVENT",
    ]
    return [fold(line) for line in lines]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    dst = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    out = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Local World Cup Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:World Cup 2026",
    ]

    count = 0
    with open(src, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not (row.get("Subject") or "").strip():
                continue
            out.extend(build_event(row))
            count += 1

    out.append("END:VCALENDAR")

    # RFC 5545 requires CRLF line endings.
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(out) + "\r\n")

    print(f"Created {dst} with {count} events")


if __name__ == "__main__":
    main()
