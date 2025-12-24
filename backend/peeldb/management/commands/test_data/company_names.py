# Company name generation data

COMPANY_PREFIXES = [
    "Tech", "Info", "Soft", "Data", "Cloud", "Digital", "Smart", "Next",
    "Prime", "Core", "Apex", "Global", "Infinite", "Bright", "Nova", "Cyber",
    "Quantum", "Rapid", "Swift", "Peak", "Vertex", "Zenith", "Alpha", "Omega",
    "Neo", "Ultra", "Mega", "Super", "Hyper", "Meta", "Syn", "Pro",
]

COMPANY_SUFFIXES = [
    "Systems", "Solutions", "Technologies", "Labs", "Infotech", "Techno",
    "Software", "Innovations", "Services", "Consulting", "Networks", "Dynamics",
    "Logic", "Ware", "Soft", "Tech", "Mind", "Edge", "Works", "Hub",
]

COMPANY_TYPE_SUFFIXES = [
    "Pvt Ltd", "Private Limited", "Solutions Pvt Ltd", "Technologies Pvt Ltd",
    "India Pvt Ltd", "Software Pvt Ltd", "IT Services", "Consulting LLP",
]

# Realistic Indian IT company name patterns
INDIAN_COMPANY_PATTERNS = [
    "{prefix}{suffix}",
    "{prefix}{suffix} {type}",
    "{lastname} {suffix}",
    "{lastname} {suffix} {type}",
    "{prefix} {suffix} India",
    "{firstname}{suffix}",
]

# Business park and address patterns
ADDRESS_PATTERNS = [
    "{number}, {park}, {area}, {city}",
    "Floor {floor}, {building}, {area}, {city}",
    "{building}, Plot {number}, {park}, {city}",
    "{number}/{floor}, {area}, {city} - {pincode}",
]

BUSINESS_PARKS = [
    "Cyber Park", "Tech Park", "IT Park", "Software Park", "Business Park",
    "Innovation Hub", "Technology Campus", "Corporate Park", "Digital Zone",
    "Techno Park", "Info Park", "Software City", "IT Tower", "Tech Tower",
]

BUILDINGS = [
    "Prestige Tower", "DLF Cyber City", "Embassy Tech Village", "RMZ Ecoworld",
    "Manyata Tech Park", "Bagmane Tech Park", "ITPL", "Electronic City",
    "Mindspace", "Raheja Mindspace", "Cyber Gateway", "Platina Tower",
    "World Trade Center", "Phoenix Market City", "Orion Mall Tower",
]

AREAS = [
    "Whitefield", "Electronic City", "Marathahalli", "Koramangala", "HSR Layout",
    "BTM Layout", "Indiranagar", "Jayanagar", "JP Nagar", "Bannerghatta Road",
    "HITEC City", "Gachibowli", "Madhapur", "Kondapur", "Jubilee Hills",
    "Banjara Hills", "Kukatpally", "Ameerpet", "Begumpet", "Secunderabad",
    "Andheri", "Powai", "BKC", "Lower Parel", "Goregaon", "Malad", "Thane",
    "Gurugram", "Noida", "Greater Noida", "Faridabad", "Ghaziabad",
    "Salt Lake", "Rajarhat", "New Town", "Sector V", "Park Street",
    "OMR", "Sholinganallur", "Perungudi", "Velachery", "Adyar", "T Nagar",
    "Kharadi", "Hinjewadi", "Baner", "Wakad", "Viman Nagar", "Magarpatta",
]

# Company profiles
COMPANY_PROFILES = [
    "Leading IT services and consulting company delivering innovative solutions.",
    "Premier software development firm specializing in enterprise applications.",
    "Cutting-edge technology company focused on digital transformation.",
    "Full-service IT solutions provider with expertise in cloud and data.",
    "Dynamic software company building next-generation applications.",
    "Innovative tech startup disrupting the industry with AI/ML solutions.",
    "Established IT services firm with a global delivery model.",
    "Boutique software consultancy known for quality and expertise.",
    "Fast-growing technology company with a focus on product development.",
    "Enterprise software company serving Fortune 500 clients.",
]
