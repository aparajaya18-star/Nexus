# All utility/helper functions
import re
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

    if not dt:
        return ""

    if dt.hour == 0 and dt.minute == 0:
        return ""

    return dt.strftime("%I:%M %p")

def format_datetime(value):
    dt = parse_iso(value)
    if not dt:
        return ""

    return dt.strftime("%d %b %Y • %I:%M %p")
