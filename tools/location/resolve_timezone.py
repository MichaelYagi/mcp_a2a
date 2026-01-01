from tools.location.get_time_data import CITY_TIMEZONES, STATE_TIMEZONES, COUNTRY_TIMEZONES, DEFAULT_TZ

def resolve_timezone(city: str, state: str, country: str) -> str:
    # Exact match first
    key = (city, state, country)
    if key in CITY_TIMEZONES:
        return CITY_TIMEZONES[key]

    if state in STATE_TIMEZONES:
        return STATE_TIMEZONES[country]

    # Country-level fallback
    if country in COUNTRY_TIMEZONES:
        return COUNTRY_TIMEZONES[country]

    # Final fallback
    return DEFAULT_TZ