from datetime import datetime

# Map timezone → location (city, state/province/prefecture, country)
TZ_TO_LOCATION = {
    "America/Vancouver": {
        "city": "Surrey",
        "state": "British Columbia",
        "country": "Canada"
    },
    "America/Toronto": {
        "city": "Toronto",
        "state": "Ontario",
        "country": "Canada"
    },
    "America/New_York": {
        "city": "New York",
        "state": "New York",
        "country": "USA"
    },
    "Europe/London": {
        "city": "London",
        "state": "England",
        "country": "UK"
    },
    "Asia/Tokyo": {
        "city": "Tokyo",
        "state": "Tokyo Prefecture",
        "country": "Japan"
    },
}

DEFAULT_FALLBACK = {
    "city": "Surrey",
    "state": "British Columbia",
    "country": "Canada"
}

def detect_default_location():
    """
    Detects the user's location based on system timezone.
    Falls back to Surrey, Canada if unknown.
    """
    local_tz = datetime.now().astimezone().tzinfo
    tz_name = getattr(local_tz, "key", None)

    if tz_name and tz_name in TZ_TO_LOCATION:
        return TZ_TO_LOCATION[tz_name]

    return DEFAULT_FALLBACK
