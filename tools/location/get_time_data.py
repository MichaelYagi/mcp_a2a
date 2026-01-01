CITY_TIMEZONES = {
    # Canada
    ("Surrey", "Canada"): "America/Vancouver",
    ("Vancouver", "Canada"): "America/Vancouver",
    ("Burnaby", "Canada"): "America/Vancouver",
    ("Richmond", "Canada"): "America/Vancouver",
    ("Calgary", "Canada"): "America/Edmonton",
    ("Edmonton", "Canada"): "America/Edmonton",
    ("Winnipeg", "Canada"): "America/Winnipeg",
    ("Toronto", "Canada"): "America/Toronto",
    ("Ottawa", "Canada"): "America/Toronto",
    ("Montreal", "Canada"): "America/Toronto",
    ("Quebec City", "Canada"): "America/Toronto",

    # USA
    ("New York", "USA"): "America/New_York",
    ("Boston", "USA"): "America/New_York",
    ("Washington", "USA"): "America/New_York",
    ("Miami", "USA"): "America/New_York",
    ("Chicago", "USA"): "America/Chicago",
    ("Houston", "USA"): "America/Chicago",
    ("Dallas", "USA"): "America/Chicago",
    ("Denver", "USA"): "America/Denver",
    ("Phoenix", "USA"): "America/Phoenix",
    ("Los Angeles", "USA"): "America/Los_Angeles",
    ("San Francisco", "USA"): "America/Los_Angeles",
    ("Seattle", "USA"): "America/Los_Angeles",

    # UK
    ("London", "UK"): "Europe/London",
    ("Manchester", "UK"): "Europe/London",
    ("Birmingham", "UK"): "Europe/London",
    ("Edinburgh", "UK"): "Europe/London",

    # Europe
    ("Paris", "France"): "Europe/Paris",
    ("Marseille", "France"): "Europe/Paris",
    ("Berlin", "Germany"): "Europe/Berlin",
    ("Munich", "Germany"): "Europe/Berlin",
    ("Rome", "Italy"): "Europe/Rome",
    ("Milan", "Italy"): "Europe/Rome",
    ("Madrid", "Spain"): "Europe/Madrid",
    ("Barcelona", "Spain"): "Europe/Madrid",
    ("Amsterdam", "Netherlands"): "Europe/Amsterdam",
    ("Brussels", "Belgium"): "Europe/Brussels",
    ("Zurich", "Switzerland"): "Europe/Zurich",
    ("Vienna", "Austria"): "Europe/Vienna",
    ("Stockholm", "Sweden"): "Europe/Stockholm",
    ("Oslo", "Norway"): "Europe/Oslo",
    ("Copenhagen", "Denmark"): "Europe/Copenhagen",
    ("Warsaw", "Poland"): "Europe/Warsaw",
    ("Prague", "Czech Republic"): "Europe/Prague",
    ("Lisbon", "Portugal"): "Europe/Lisbon",
    ("Athens", "Greece"): "Europe/Athens",

    # Japan
    ("Tokyo", "Japan"): "Asia/Tokyo",
    ("Yokohama", "Japan"): "Asia/Tokyo",
    ("Osaka", "Japan"): "Asia/Tokyo",
    ("Nagoya", "Japan"): "Asia/Tokyo",
    ("Sapporo", "Japan"): "Asia/Tokyo",
    ("Fukuoka", "Japan"): "Asia/Tokyo",
    ("Chigasaki", "Japan"): "Asia/Tokyo",

    # East Asia
    ("Seoul", "South Korea"): "Asia/Seoul",
    ("Busan", "South Korea"): "Asia/Seoul",
    ("Shanghai", "China"): "Asia/Shanghai",
    ("Beijing", "China"): "Asia/Shanghai",
    ("Shenzhen", "China"): "Asia/Shanghai",
    ("Taipei", "Taiwan"): "Asia/Taipei",
    ("Hong Kong", "Hong Kong"): "Asia/Hong_Kong",

    # Southeast Asia
    ("Singapore", "Singapore"): "Asia/Singapore",
    ("Kuala Lumpur", "Malaysia"): "Asia/Kuala_Lumpur",
    ("Bangkok", "Thailand"): "Asia/Bangkok",
    ("Ho Chi Minh City", "Vietnam"): "Asia/Ho_Chi_Minh",
    ("Hanoi", "Vietnam"): "Asia/Bangkok",
    ("Manila", "Philippines"): "Asia/Manila",
    ("Jakarta", "Indonesia"): "Asia/Jakarta",

    # South Asia
    ("Delhi", "India"): "Asia/Kolkata",
    ("Mumbai", "India"): "Asia/Kolkata",
    ("Bangalore", "India"): "Asia/Kolkata",
    ("Karachi", "Pakistan"): "Asia/Karachi",
    ("Dhaka", "Bangladesh"): "Asia/Dhaka",

    # Middle East
    ("Dubai", "UAE"): "Asia/Dubai",
    ("Abu Dhabi", "UAE"): "Asia/Dubai",
    ("Riyadh", "Saudi Arabia"): "Asia/Riyadh",
    ("Doha", "Qatar"): "Asia/Qatar",
    ("Kuwait City", "Kuwait"): "Asia/Kuwait",
    ("Jerusalem", "Israel"): "Asia/Jerusalem",

    # Africa
    ("Johannesburg", "South Africa"): "Africa/Johannesburg",
    ("Cape Town", "South Africa"): "Africa/Johannesburg",
    ("Cairo", "Egypt"): "Africa/Cairo",
    ("Lagos", "Nigeria"): "Africa/Lagos",
    ("Nairobi", "Kenya"): "Africa/Nairobi",
    ("Casablanca", "Morocco"): "Africa/Casablanca",

    # Oceania
    ("Sydney", "Australia"): "Australia/Sydney",
    ("Melbourne", "Australia"): "Australia/Melbourne",
    ("Brisbane", "Australia"): "Australia/Brisbane",
    ("Perth", "Australia"): "Australia/Perth",
    ("Auckland", "New Zealand"): "Pacific/Auckland",
    ("Wellington", "New Zealand"): "Pacific/Auckland",
}

STATE_TIMEZONES = {
    # Canada (Provinces & Territories)
    ("British Columbia", "Canada"): "America/Vancouver",
    ("Alberta", "Canada"): "America/Edmonton",
    ("Saskatchewan", "Canada"): "America/Regina",
    ("Manitoba", "Canada"): "America/Winnipeg",
    ("Ontario", "Canada"): "America/Toronto",
    ("Quebec", "Canada"): "America/Toronto",
    ("New Brunswick", "Canada"): "America/Moncton",
    ("Nova Scotia", "Canada"): "America/Halifax",
    ("Prince Edward Island", "Canada"): "America/Halifax",
    ("Newfoundland and Labrador", "Canada"): "America/St_Johns",
    ("Yukon", "Canada"): "America/Whitehorse",
    ("Northwest Territories", "Canada"): "America/Yellowknife",
    ("Nunavut", "Canada"): "America/Iqaluit",

    # USA (States)
    ("New York", "USA"): "America/New_York",
    ("Massachusetts", "USA"): "America/New_York",
    ("Florida", "USA"): "America/New_York",
    ("District of Columbia", "USA"): "America/New_York",
    ("Illinois", "USA"): "America/Chicago",
    ("Texas", "USA"): "America/Chicago",
    ("Colorado", "USA"): "America/Denver",
    ("Arizona", "USA"): "America/Phoenix",
    ("California", "USA"): "America/Los_Angeles",
    ("Washington", "USA"): "America/Los_Angeles",
    ("Oregon", "USA"): "America/Los_Angeles",

    # UK (Countries)
    ("England", "UK"): "Europe/London",
    ("Scotland", "UK"): "Europe/London",
    ("Wales", "UK"): "Europe/London",
    ("Northern Ireland", "UK"): "Europe/London",

    # Australia (States & Territories)
    ("New South Wales", "Australia"): "Australia/Sydney",
    ("Victoria", "Australia"): "Australia/Melbourne",
    ("Queensland", "Australia"): "Australia/Brisbane",
    ("Western Australia", "Australia"): "Australia/Perth",
    ("South Australia", "Australia"): "Australia/Adelaide",
    ("Tasmania", "Australia"): "Australia/Hobart",
    ("Northern Territory", "Australia"): "Australia/Darwin",
    ("Australian Capital Territory", "Australia"): "Australia/Sydney",

    # India (States share one timezone)
    ("Maharashtra", "India"): "Asia/Kolkata",
    ("Karnataka", "India"): "Asia/Kolkata",
    ("Delhi", "India"): "Asia/Kolkata",
    ("Tamil Nadu", "India"): "Asia/Kolkata",
    ("West Bengal", "India"): "Asia/Kolkata",

    # Japan (Prefectures share one timezone)
    ("Tokyo", "Japan"): "Asia/Tokyo",
    ("Kanagawa", "Japan"): "Asia/Tokyo",
    ("Osaka", "Japan"): "Asia/Tokyo",
    ("Hokkaido", "Japan"): "Asia/Tokyo",
    ("Aichi", "Japan"): "Asia/Tokyo",
    ("Fukuoka", "Japan"): "Asia/Tokyo",

    # China (Provinces share one timezone)
    ("Guangdong", "China"): "Asia/Shanghai",
    ("Beijing", "China"): "Asia/Shanghai",
    ("Shanghai", "China"): "Asia/Shanghai",
    ("Zhejiang", "China"): "Asia/Shanghai",
    ("Jiangsu", "China"): "Asia/Shanghai",

    # Middle East (Regions share country timezone)
    ("Dubai", "UAE"): "Asia/Dubai",
    ("Abu Dhabi", "UAE"): "Asia/Dubai",
    ("Riyadh Province", "Saudi Arabia"): "Asia/Riyadh",
    ("Doha Municipality", "Qatar"): "Asia/Qatar",
    ("Kuwait", "Kuwait"): "Asia/Kuwait",
    ("Jerusalem District", "Israel"): "Asia/Jerusalem",

    # Africa (Regions share country timezone)
    ("Gauteng", "South Africa"): "Africa/Johannesburg",
    ("Western Cape", "South Africa"): "Africa/Johannesburg",
    ("Cairo Governorate", "Egypt"): "Africa/Cairo",
    ("Lagos State", "Nigeria"): "Africa/Lagos",
    ("Nairobi County", "Kenya"): "Africa/Nairobi",
    ("Casablanca-Settat", "Morocco"): "Africa/Casablanca",

    # Southeast Asia (Regions share country timezone)
    ("Bangkok", "Thailand"): "Asia/Bangkok",
    ("Ho Chi Minh", "Vietnam"): "Asia/Ho_Chi_Minh",
    ("Hanoi", "Vietnam"): "Asia/Bangkok",
    ("Metro Manila", "Philippines"): "Asia/Manila",
    ("Jakarta", "Indonesia"): "Asia/Jakarta",
    ("Kuala Lumpur", "Malaysia"): "Asia/Kuala_Lumpur",
}

COUNTRY_TIMEZONES = {
    # North America
    "Canada": "America/Toronto",          # default; west coast cities override via CITY_TIMEZONES
    "USA": "America/New_York",
    "Mexico": "America/Mexico_City",

    # South America
    "Brazil": "America/Sao_Paulo",
    "Argentina": "America/Argentina/Buenos_Aires",
    "Chile": "America/Santiago",
    "Colombia": "America/Bogota",
    "Peru": "America/Lima",

    # Europe
    "UK": "Europe/London",
    "Ireland": "Europe/Dublin",
    "France": "Europe/Paris",
    "Germany": "Europe/Berlin",
    "Spain": "Europe/Madrid",
    "Italy": "Europe/Rome",
    "Netherlands": "Europe/Amsterdam",
    "Belgium": "Europe/Brussels",
    "Sweden": "Europe/Stockholm",
    "Norway": "Europe/Oslo",
    "Finland": "Europe/Helsinki",
    "Denmark": "Europe/Copenhagen",
    "Poland": "Europe/Warsaw",
    "Czech Republic": "Europe/Prague",
    "Austria": "Europe/Vienna",
    "Switzerland": "Europe/Zurich",
    "Portugal": "Europe/Lisbon",
    "Greece": "Europe/Athens",
    "Turkey": "Europe/Istanbul",

    # Middle East
    "Israel": "Asia/Jerusalem",
    "Saudi Arabia": "Asia/Riyadh",
    "UAE": "Asia/Dubai",
    "Qatar": "Asia/Qatar",
    "Kuwait": "Asia/Kuwait",

    # Africa
    "South Africa": "Africa/Johannesburg",
    "Egypt": "Africa/Cairo",
    "Nigeria": "Africa/Lagos",
    "Kenya": "Africa/Nairobi",
    "Morocco": "Africa/Casablanca",

    # Asia
    "Japan": "Asia/Tokyo",
    "South Korea": "Asia/Seoul",
    "China": "Asia/Shanghai",
    "Taiwan": "Asia/Taipei",
    "Hong Kong": "Asia/Hong_Kong",
    "Singapore": "Asia/Singapore",
    "Malaysia": "Asia/Kuala_Lumpur",
    "Thailand": "Asia/Bangkok",
    "Vietnam": "Asia/Ho_Chi_Minh",
    "Philippines": "Asia/Manila",
    "India": "Asia/Kolkata",
    "Pakistan": "Asia/Karachi",
    "Bangladesh": "Asia/Dhaka",
    "Indonesia": "Asia/Jakarta",

    # Oceania
    "Australia": "Australia/Sydney",
    "New Zealand": "Pacific/Auckland",
}

DEFAULT_TZ = "UTC"   # safe fallback