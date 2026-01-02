from typing import Optional
from tools.location.detect_location import detect_default_location

def resolve_location(city: Optional[str], state: Optional[str], country: Optional[str]):
    """
    Normalizes location input. Only uses defaults if NO location info is provided.
    """
    # Only use system defaults if EVERYTHING is missing
    if not city and not state and not country:
        return detect_default_location()

    # Otherwise, trust the input and don't mix in Surrey/BC defaults
    return {
        "city": city.strip() if city else None,
        "state": state.strip() if state else None,
        "country": country.strip() if country else None
    }