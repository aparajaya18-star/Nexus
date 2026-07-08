# All utility/helper functions

from datetime import datetime

def parse_iso(value):
    if not value:
        return None
    return datetime.fromisoformat(value)

def format_date(value):
    dt = parse_iso(value)
    return dt.strftime("%d %b %Y") if dt else ""

def format_time(value):
    dt = parse_iso(value)
    return dt.strftime("%I:%M %p") if dt else ""