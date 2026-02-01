"""
Script to load education lookup data directly into the database
Bypasses Haystack signal processor to avoid Elasticsearch dependency
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from peeldb.models import Qualification, Degree, EducationInstitue, City

def load_qualifications():
    """Load qualification data"""
    qualifications = [
        {"id": 1, "name": "MBA", "status": "Active", "slug": "mba"},
        {"id": 2, "name": "B.Tech", "status": "Active", "slug": "btech"},
        {"id": 4, "name": "B.A", "status": "Active", "slug": "ba"},
        {"id": 5, "name": "B.Arch", "status": "Active", "slug": "barch"},
        {"id": 6, "name": "B.B.A", "status": "Active", "slug": "bba"},
        {"id": 7, "name": "BCA", "status": "Active", "slug": "bca"},
        {"id": 8, "name": "B.Com", "status": "Active", "slug": "bcom"},
        {"id": 9, "name": "BDS", "status": "Active", "slug": "bds"},
        {"id": 11, "name": "BHM", "status": "Active", "slug": "bhm"},
        {"id": 13, "name": "BL LLB", "status": "Active", "slug": "bl-llb"},
        {"id": 14, "name": "B.Pharm", "status": "Active", "slug": "bpharm"},
        {"id": 15, "name": "B.Sc", "status": "Active", "slug": "bsc"},
        {"id": 16, "name": "M.Tech", "status": "Active", "slug": "mtech"},
        {"id": 17, "name": "M.A", "status": "Active", "slug": "ma"},
        {"id": 18, "name": "M.Sc", "status": "Active", "slug": "msc"},
        {"id": 19, "name": "MCA", "status": "Active", "slug": "mca"},
        {"id": 20, "name": "M.Com", "status": "Active", "slug": "mcom"},
        {"id": 21, "name": "Ph.D", "status": "Active", "slug": "phd"},
        {"id": 22, "name": "Diploma", "status": "Active", "slug": "diploma"},
        {"id": 23, "name": "12th Pass", "status": "Active", "slug": "12th-pass"},
        {"id": 24, "name": "10th Pass", "status": "Active", "slug": "10th-pass"},
    ]

    created_count = 0
    for qual_data in qualifications:
        qual, created = Qualification.objects.update_or_create(
            id=qual_data["id"],
            defaults={
                "name": qual_data["name"],
                "status": qual_data["status"],
                "slug": qual_data["slug"]
            }
        )
        if created:
            created_count += 1

    print(f"Loaded {len(qualifications)} qualifications ({created_count} new)")
    return qualifications


def load_degrees():
    """Load degree data"""
    # Get qualifications
    btech = Qualification.objects.filter(slug="btech").first()
    mtech = Qualification.objects.filter(slug="mtech").first()
    mba = Qualification.objects.filter(slug="mba").first()
    bsc = Qualification.objects.filter(slug="bsc").first()
    msc = Qualification.objects.filter(slug="msc").first()
    bca = Qualification.objects.filter(slug="bca").first()
    mca = Qualification.objects.filter(slug="mca").first()
    bcom = Qualification.objects.filter(slug="bcom").first()
    ba = Qualification.objects.filter(slug="ba").first()
    diploma = Qualification.objects.filter(slug="diploma").first()

    degrees_data = []

    # B.Tech degrees
    if btech:
        btech_specs = [
            "Computer Science", "Information Technology", "Electronics",
            "Electrical", "Mechanical", "Civil", "Chemical", "Biotechnology"
        ]
        for spec in btech_specs:
            degrees_data.append({
                "qualification": btech,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # M.Tech degrees
    if mtech:
        mtech_specs = [
            "Computer Science", "Information Technology", "Software Engineering",
            "Data Science", "Artificial Intelligence", "Machine Learning"
        ]
        for spec in mtech_specs:
            degrees_data.append({
                "qualification": mtech,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # MBA degrees
    if mba:
        mba_specs = [
            "Finance", "Marketing", "Human Resources", "Operations",
            "Information Technology", "General Management"
        ]
        for spec in mba_specs:
            degrees_data.append({
                "qualification": mba,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # B.Sc degrees
    if bsc:
        bsc_specs = [
            "Computer Science", "Information Technology", "Mathematics",
            "Physics", "Chemistry", "Biology"
        ]
        for spec in bsc_specs:
            degrees_data.append({
                "qualification": bsc,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # M.Sc degrees
    if msc:
        msc_specs = [
            "Computer Science", "Information Technology", "Data Science",
            "Mathematics", "Physics"
        ]
        for spec in msc_specs:
            degrees_data.append({
                "qualification": msc,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # BCA degrees
    if bca:
        degrees_data.append({
            "qualification": bca,
            "specialization": "Computer Applications",
            "degree_type": "Permanent"
        })

    # MCA degrees
    if mca:
        degrees_data.append({
            "qualification": mca,
            "specialization": "Computer Applications",
            "degree_type": "Permanent"
        })

    # B.Com degrees
    if bcom:
        bcom_specs = ["General", "Computers", "Accounting", "Finance"]
        for spec in bcom_specs:
            degrees_data.append({
                "qualification": bcom,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # B.A degrees
    if ba:
        ba_specs = ["English", "Economics", "Psychology", "Political Science"]
        for spec in ba_specs:
            degrees_data.append({
                "qualification": ba,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    # Diploma degrees
    if diploma:
        diploma_specs = [
            "Computer Science", "Mechanical", "Electrical", "Civil"
        ]
        for spec in diploma_specs:
            degrees_data.append({
                "qualification": diploma,
                "specialization": spec,
                "degree_type": "Permanent"
            })

    created_count = 0
    for degree_data in degrees_data:
        degree, created = Degree.objects.get_or_create(
            degree_name=degree_data["qualification"],
            specialization=degree_data["specialization"],
            defaults={"degree_type": degree_data["degree_type"]}
        )
        if created:
            created_count += 1

    print(f"Loaded {len(degrees_data)} degrees ({created_count} new)")


def load_institutes():
    """Load education institute data"""
    institutes = [
        {"name": "Indian Institute of Technology Delhi", "address": "Hauz Khas", "city": "New Delhi"},
        {"name": "Indian Institute of Technology Bombay", "address": "Powai", "city": "Mumbai"},
        {"name": "Indian Institute of Technology Madras", "address": "Guindy", "city": "Chennai"},
        {"name": "Indian Institute of Technology Kanpur", "address": "Kalyanpur", "city": "Kanpur"},
        {"name": "Indian Institute of Technology Kharagpur", "address": "Kharagpur", "city": "Kharagpur"},
        {"name": "Indian Institute of Technology Hyderabad", "address": "Kandi", "city": "Hyderabad"},
        {"name": "Indian Institute of Technology Roorkee", "address": "Roorkee", "city": "Roorkee"},
        {"name": "BITS Pilani", "address": "Pilani Campus", "city": "Pilani"},
        {"name": "NIT Trichy", "address": "Tiruchirappalli", "city": "Tiruchirappalli"},
        {"name": "NIT Warangal", "address": "Warangal", "city": "Warangal"},
        {"name": "IIIT Hyderabad", "address": "Gachibowli", "city": "Hyderabad"},
        {"name": "Delhi University", "address": "North Campus", "city": "New Delhi"},
        {"name": "Jawaharlal Nehru University", "address": "New Mehrauli Road", "city": "New Delhi"},
        {"name": "Anna University", "address": "Guindy", "city": "Chennai"},
        {"name": "Osmania University", "address": "Amberpet", "city": "Hyderabad"},
        {"name": "University of Mumbai", "address": "Fort", "city": "Mumbai"},
        {"name": "Bangalore University", "address": "Jnana Bharathi", "city": "Bangalore"},
        {"name": "Pune University", "address": "Ganeshkhind", "city": "Pune"},
        {"name": "Jadavpur University", "address": "Jadavpur", "city": "Kolkata"},
        {"name": "Calcutta University", "address": "College Street", "city": "Kolkata"},
    ]

    created_count = 0
    for inst_data in institutes:
        # Try to find the city by name (case-insensitive)
        city_name = inst_data.get("city", "")
        city_obj = City.objects.filter(name__iexact=city_name).first() if city_name else None

        inst, created = EducationInstitue.objects.get_or_create(
            name=inst_data["name"],
            defaults={
                "address": inst_data["address"],
                "city": city_obj
            }
        )
        if created:
            created_count += 1

    print(f"Loaded {len(institutes)} institutes ({created_count} new)")


if __name__ == "__main__":
    print("Loading education lookup data...")
    print("-" * 50)

    # Disconnect Haystack signals temporarily
    from django.db.models import signals as django_signals

    # Try to disconnect the haystack signal processor
    try:
        # Haystack uses post_save and post_delete signals
        django_signals.post_save.receivers = [
            r for r in django_signals.post_save.receivers
            if 'haystack' not in str(r)
        ]
        django_signals.post_delete.receivers = [
            r for r in django_signals.post_delete.receivers
            if 'haystack' not in str(r)
        ]
        print("Temporarily disabled Haystack signals")
    except Exception as e:
        print(f"Could not disable Haystack signals: {e}")

    load_qualifications()
    load_degrees()
    load_institutes()

    print("-" * 50)
    print("Done! Education lookup data loaded successfully.")

