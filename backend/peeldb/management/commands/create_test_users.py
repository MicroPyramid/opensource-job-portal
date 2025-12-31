"""
Management command to create test users with known credentials.

Usage:
    python manage.py create_test_users
    python manage.py create_test_users --clear
    python manage.py create_test_users --config /path/to/custom-users.json
"""
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from peeldb.models import (
    Company,
    Country,
    User,
    City,
    Skill,
    Industry,
    Qualification,
    Language,
    TechnicalSkill,
    EmploymentHistory,
    EducationDetails,
    EducationInstitue,
    Degree,
    UserLanguage,
    JobPost,
)

# Default config file path
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "fixtures" / "test-users.json"


class Command(BaseCommand):
    help = "Creates test users with known credentials for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing test users and recreate them",
        )
        parser.add_argument(
            "--config",
            type=str,
            default=str(DEFAULT_CONFIG_PATH),
            help="Path to JSON config file with test user definitions",
        )

    def handle(self, *args, **options):
        # Load config
        config_path = Path(options["config"])
        if not config_path.exists():
            raise CommandError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            self.test_users = json.load(f)

        self.stdout.write(f"Loading test users from: {config_path}")

        # Disable Haystack signals during data creation
        signal_processor = apps.get_app_config("haystack").signal_processor
        signal_processor.teardown()

        try:
            if options["clear"]:
                self._clear_test_users()

            self._validate_fixtures_loaded()

            # Load reference data
            self.cities = list(City.objects.filter(status="Enabled"))
            self.skills = list(Skill.objects.filter(status="Active"))
            self.industries = list(Industry.objects.filter(status="Active"))
            self.qualifications = list(Qualification.objects.all())
            self.languages = list(Language.objects.all())
            self.country = Country.objects.filter(status="Enabled").first()

            with transaction.atomic():
                if "superuser" in self.test_users:
                    self._create_superuser(self.test_users["superuser"])
                # Create company_admin first (creates the company)
                if "company_admin" in self.test_users:
                    self._create_company_admin(self.test_users["company_admin"])
                # Then create recruiter (references existing company)
                if "recruiter" in self.test_users:
                    self._create_recruiter(self.test_users["recruiter"])
                if "individual" in self.test_users:
                    self._create_individual(self.test_users["individual"])
                if "jobseeker" in self.test_users:
                    self._create_jobseeker(self.test_users["jobseeker"])

            self.stdout.write(
                self.style.SUCCESS("\nTest users created/updated successfully!")
            )

        finally:
            signal_processor.setup()

    def _validate_fixtures_loaded(self):
        """Ensure reference data from fixtures exists."""
        if not City.objects.filter(status="Enabled").exists():
            raise CommandError(
                "No cities found. Run 'python manage.py load_initial_data' first."
            )
        if not Skill.objects.filter(status="Active").exists():
            raise CommandError(
                "No skills found. Run 'python manage.py load_initial_data' first."
            )

    def _clear_test_users(self):
        """Clear existing test users and their companies (except superuser)."""
        self.stdout.write("Clearing existing test users...")

        # First pass: delete users (except superuser), collect companies to delete
        companies_to_delete = set()

        for user_type, data in self.test_users.items():
            # Skip superuser - don't delete it
            if user_type == "superuser":
                self.stdout.write(f"  Skipping superuser: {data['email']}")
                continue

            user = User.objects.filter(email=data["email"]).first()
            if user:
                # Delete job posts first
                JobPost.objects.filter(user=user).delete()
                # Track company for deletion (only if owned by company_admin)
                if user.company and user_type == "company_admin":
                    companies_to_delete.add(user.company.id)
                user.delete()
                self.stdout.write(f"  Deleted {user_type}: {data['email']}")

        # Second pass: delete companies (after all users are deleted)
        for company_id in companies_to_delete:
            company = Company.objects.filter(id=company_id).first()
            if company:
                company.delete()
                self.stdout.write(f"  Deleted company: {company.name}")

        self.stdout.write(self.style.SUCCESS("Test users cleared."))

    def _get_city(self, name):
        """Get city by name or return first available city."""
        city = City.objects.filter(name__icontains=name, status="Enabled").first()
        if not city:
            city = self.cities[0] if self.cities else None
        return city

    def _get_skills_by_name(self, skill_names):
        """Get skills by name."""
        skills = []
        for name in skill_names:
            skill = Skill.objects.filter(name__icontains=name, status="Active").first()
            if skill:
                skills.append(skill)
        return skills

    def _get_industries_by_name(self, industry_names):
        """Get industries by name."""
        industries = []
        for name in industry_names:
            industry = Industry.objects.filter(
                name__icontains=name, status="Active"
            ).first()
            if industry:
                industries.append(industry)
        return industries

    def _create_superuser(self, data):
        """Create or update the superuser account."""
        user = User.objects.filter(email=data["email"]).first()
        if user:
            # Update existing superuser
            user.first_name = data.get("first_name", "Admin")
            user.last_name = data.get("last_name", "User")
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(f"  Superuser updated: {data['email']}")
        else:
            # Generate random password for new superuser
            password = secrets.token_urlsafe(16)

            user = User.objects.create_superuser(
                username=data.get("username", data["email"].split("@")[0]),
                email=data["email"],
                password=password,
                first_name=data.get("first_name", "Admin"),
                last_name=data.get("last_name", "User"),
            )

            self.stdout.write(self.style.SUCCESS(f"\n  Superuser created: {data['email']}"))
            self.stdout.write(self.style.WARNING(f"  Password: {password}"))
            self.stdout.write("  (Save this password - it won't be shown again!)\n")

    def _create_company_admin(self, data):
        """Create or update the company admin account (creates/owns the company)."""
        city = self._get_city(data.get("city", "Hyderabad"))

        user = User.objects.filter(email=data["email"]).first()
        created = False

        company_data = data.get("company", {})
        company_slug = company_data.get("slug", data.get("username", "test") + "-company")

        # Get or create company
        company, _ = Company.objects.get_or_create(
            slug=company_slug,
            defaults={
                "name": company_data.get("name", "Test Company"),
                "website": company_data.get("website", ""),
                "address": company_data.get("address", ""),
                "profile": company_data.get("profile", ""),
                "phone_number": company_data.get("phone_number", ""),
                "email": company_data.get("email", data["email"]),
                "size": company_data.get("size", "11-20"),
                "company_type": company_data.get("company_type", "Company"),
                "is_active": True,
            },
        )

        if not user:
            # Create company admin user
            user = User.objects.create(
                username=data.get("username", data["email"].split("@")[0]),
                email=data["email"],
                company=company,
            )
            created = True

        # Update user fields
        user.first_name = data.get("first_name", "Company")
        user.last_name = data.get("last_name", "Admin")
        user.user_type = "EM"
        user.company = company
        user.is_active = True
        user.is_admin = True  # Always admin for company_admin
        user.mobile_verified = True
        user.email_verified = True
        user.city = city
        user.state = city.state if city else None
        user.country = city.state.country if city and city.state else None
        user.mobile = data.get("mobile", "")
        user.profile_description = data.get("profile_description", "")
        user.job_title = data.get("job_title", "Company Admin")
        user.set_password(data.get("password", "testpass123"))
        user.save()

        # Add industries and skills
        industries = self._get_industries_by_name(data.get("industries", []))
        if industries:
            user.industry.set(industries)

        skills = self._get_skills_by_name(data.get("skills", []))
        if skills:
            user.technical_skills.set(skills)

        # Create job posts
        job_posts = self._create_job_posts(user, data.get("job_posts", []))

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"  Company Admin {action}: {data['email']} / {data.get('password', 'testpass123')}")
        )
        if job_posts:
            self.stdout.write(f"    Created {len(job_posts)} job posts")

    def _create_recruiter(self, data):
        """Create or update the company recruiter account (non-admin, uses existing company)."""
        city = self._get_city(data.get("city", "Hyderabad"))

        user = User.objects.filter(email=data["email"]).first()
        created = False

        # Look up existing company by slug (created by company_admin)
        company_slug = data.get("company_slug")
        company = None
        if company_slug:
            company = Company.objects.filter(slug=company_slug).first()
            if not company:
                self.stdout.write(
                    self.style.WARNING(f"  Warning: Company with slug '{company_slug}' not found. Recruiter will have no company.")
                )

        if not user:
            # Create recruiter user
            user = User.objects.create(
                username=data.get("username", data["email"].split("@")[0]),
                email=data["email"],
                company=company,
            )
            created = True

        # Update user fields
        user.first_name = data.get("first_name", "Recruiter")
        user.last_name = data.get("last_name", "User")
        user.user_type = "EM"
        user.company = company
        user.is_active = True
        user.is_admin = data.get("is_admin", False)  # Non-admin by default for recruiter
        user.mobile_verified = True
        user.email_verified = True
        user.city = city
        user.state = city.state if city else None
        user.country = city.state.country if city and city.state else None
        user.mobile = data.get("mobile", "")
        user.profile_description = data.get("profile_description", "")
        user.job_title = data.get("job_title", "Recruiter")
        user.set_password(data.get("password", "testpass123"))
        user.save()

        # Add industries and skills
        industries = self._get_industries_by_name(data.get("industries", []))
        if industries:
            user.industry.set(industries)

        skills = self._get_skills_by_name(data.get("skills", []))
        if skills:
            user.technical_skills.set(skills)

        # Create job posts
        job_posts = self._create_job_posts(user, data.get("job_posts", []))

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"  Recruiter {action}: {data['email']} / {data.get('password', 'testpass123')}")
        )
        if job_posts:
            self.stdout.write(f"    Created {len(job_posts)} job posts")

    def _create_individual(self, data):
        """Create or update the individual/consultant recruiter account (no company)."""
        city = self._get_city(data.get("city", "Bangalore"))

        user = User.objects.filter(email=data["email"]).first()
        created = False

        if not user:
            # Create individual recruiter user (no company)
            user = User.objects.create(
                username=data.get("username", data["email"].split("@")[0]),
                email=data["email"],
                company=None,  # Individual recruiter has no company
            )
            created = True

        # Update user fields
        user.first_name = data.get("first_name", "Individual")
        user.last_name = data.get("last_name", "Recruiter")
        user.user_type = "EM"
        user.company = None  # Ensure no company
        user.is_active = True
        user.is_admin = False  # Individual has no admin role
        user.mobile_verified = True
        user.email_verified = True
        user.city = city
        user.state = city.state if city else None
        user.country = city.state.country if city and city.state else None
        user.mobile = data.get("mobile", "")
        user.profile_description = data.get("profile_description", "")
        user.job_title = data.get("job_title", "Independent Recruiter")
        user.set_password(data.get("password", "testpass123"))
        user.save()

        # Add industries and skills
        industries = self._get_industries_by_name(data.get("industries", []))
        if industries:
            user.industry.set(industries)

        skills = self._get_skills_by_name(data.get("skills", []))
        if skills:
            user.technical_skills.set(skills)

        # Create job posts
        job_posts = self._create_job_posts(user, data.get("job_posts", []))

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"  Individual {action}: {data['email']} / {data.get('password', 'testpass123')}")
        )
        if job_posts:
            self.stdout.write(f"    Created {len(job_posts)} job posts")

    def _create_job_posts(self, user, job_posts_data):
        """Create job posts for a recruiter."""
        # Clear existing job posts for this user first
        JobPost.objects.filter(user=user).delete()

        created_posts = []
        for i, job_data in enumerate(job_posts_data):
            city = self._get_city(job_data.get("city", "Hyderabad"))
            title = job_data.get("title", "Software Developer")
            slug = slugify(f"{title}-{user.username}-{i}")

            # Check if slug exists and make it unique
            base_slug = slug
            counter = 1
            while JobPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            job = JobPost.objects.create(
                user=user,
                company=user.company,  # None for individual recruiters
                title=title,
                slug=slug,
                description=job_data.get("description", f"Job posting for {title}"),
                vacancies=job_data.get("vacancies", 1),
                min_year=job_data.get("min_year", 0),
                max_year=job_data.get("max_year", 5),
                min_month=0,
                max_month=0,
                min_salary=job_data.get("min_salary", 0),
                max_salary=job_data.get("max_salary", 0),
                salary_type="Year",
                job_type=job_data.get("job_type", "full-time"),
                work_mode=job_data.get("work_mode", "in-office"),
                status="Live",
                published_on=timezone.now(),
                fresher=(job_data.get("min_year", 0) == 0),
                country=self.country,
                meta_title=f"{title} Jobs",
                meta_description=f"Apply for {title} position.",
                company_name=user.company.name if user.company else "",
                company_address=user.company.address if user.company else "",
                company_description=user.company.profile if user.company else "",
            )

            # Add location
            if city:
                job.location.add(city)

            # Add skills
            skills = self._get_skills_by_name(job_data.get("skills", []))
            if skills:
                job.skills.set(skills)

            # Add industries
            industries = self._get_industries_by_name(job_data.get("industries", ["IT"]))
            if industries:
                job.industry.set(industries)

            created_posts.append(job)

        return created_posts

    def _create_jobseeker(self, data):
        """Create or update the jobseeker account with full profile."""
        city = self._get_city(data.get("city", "Hyderabad"))

        user = User.objects.filter(email=data["email"]).first()
        created = False

        if not user:
            user = User.objects.create(
                username=data.get("username", data["email"].split("@")[0]),
                email=data["email"],
            )
            created = True

        # Calculate DOB based on experience
        exp_years = data.get("experience_years", 5)
        age = 22 + exp_years + 2  # 22 at graduation + experience + buffer
        dob = (datetime.now() - timedelta(days=age * 365 + 100)).date()

        # Update user fields
        user.first_name = data.get("first_name", "Job")
        user.last_name = data.get("last_name", "Seeker")
        user.user_type = "JS"
        user.is_active = True
        user.mobile_verified = True
        user.email_verified = True
        user.city = city
        user.current_city = city
        user.state = city.state if city else None
        user.country = city.state.country if city and city.state else None
        user.mobile = data.get("mobile", "")
        user.year = str(data.get("experience_years", 5))
        user.month = str(data.get("experience_months", 0))
        user.current_salary = str(data.get("current_salary", ""))
        user.expected_salary = str(data.get("expected_salary", ""))
        user.dob = dob
        user.gender = data.get("gender", "M")
        user.profile_description = data.get("profile_description", "")
        user.resume_title = data.get("resume_title", f"{user.first_name} {user.last_name} - Resume")
        user.is_looking_for_job = data.get("is_looking_for_job", True)
        user.is_open_to_offers = data.get("is_open_to_offers", True)
        user.relocation = data.get("relocation", True)
        user.notice_period = data.get("notice_period", "1 Month")
        user.set_password(data.get("password", "testpass123"))
        user.save()

        # Add preferred cities
        preferred_cities = []
        for city_name in data.get("preferred_cities", []):
            c = self._get_city(city_name)
            if c:
                preferred_cities.append(c)
        if preferred_cities:
            user.preferred_city.set(preferred_cities)

        # Create/update technical skills
        self._create_jobseeker_skills(user, data.get("skills", []))

        # Create/update employment history
        self._create_jobseeker_employment(user, data.get("employment_history", []))

        # Create/update education
        if "education" in data:
            self._create_jobseeker_education(user, data["education"])

        # Create/update language skills
        self._create_jobseeker_languages(user, data.get("languages", []))

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"  Jobseeker {action}: {data['email']} / {data.get('password', 'testpass123')}")
        )

    def _create_jobseeker_skills(self, user, skills_data):
        """Create technical skills for the jobseeker."""
        # Clear existing skills first
        user.skills.clear()

        tech_skills = []
        for skill_info in skills_data:
            skill_name = skill_info if isinstance(skill_info, str) else skill_info.get("name")
            skill = Skill.objects.filter(
                name__iexact=skill_name, status="Active"
            ).first()
            if not skill:
                skill = Skill.objects.filter(
                    name__icontains=skill_name, status="Active"
                ).first()
            if skill:
                years = skill_info.get("years", 1) if isinstance(skill_info, dict) else 1
                proficiency = skill_info.get("proficiency", "Good") if isinstance(skill_info, dict) else "Good"
                is_major = skill_info.get("is_major", False) if isinstance(skill_info, dict) else False

                tech_skill = TechnicalSkill.objects.create(
                    skill=skill,
                    year=years,
                    month=6,
                    proficiency=proficiency,
                    is_major=is_major,
                )
                tech_skills.append(tech_skill)

        if tech_skills:
            user.skills.set(tech_skills)

    def _create_jobseeker_employment(self, user, employment_data):
        """Create employment history for the jobseeker."""
        # Clear existing employment history first
        user.employment_history.clear()

        now = datetime.now().date()
        history = []

        for emp_info in employment_data:
            years_ago_start = emp_info.get("years_ago_start", 0)
            years_ago_end = emp_info.get("years_ago_end", None)
            is_current = emp_info.get("current_job", False)

            from_date = now - timedelta(days=int(years_ago_start * 365))
            to_date = None if is_current else (now - timedelta(days=int(years_ago_end * 365)) if years_ago_end else None)

            emp = EmploymentHistory.objects.create(
                company=emp_info.get("company", "Unknown Company"),
                designation=emp_info.get("designation", "Employee"),
                from_date=from_date,
                to_date=to_date,
                current_job=is_current,
                job_profile=emp_info.get("job_profile", ""),
            )
            history.append(emp)

        if history:
            user.employment_history.set(history)

    def _create_jobseeker_education(self, user, education_data):
        """Create education details for the jobseeker."""
        # Clear existing education first
        user.education.clear()

        # Get or create institute
        institute, _ = EducationInstitue.objects.get_or_create(
            name=education_data.get("institute", "Unknown Institute"),
            defaults={
                "address": education_data.get("institute_address", ""),
            },
        )

        # Get qualification
        qual_name = education_data.get("qualification", "B.Tech")
        qualification = Qualification.objects.filter(
            name__icontains=qual_name
        ).first()
        if not qualification:
            qualification = self.qualifications[0] if self.qualifications else None

        if qualification:
            # Get first matching degree or create one
            degree = Degree.objects.filter(degree_name=qualification).first()
            if not degree:
                degree = Degree.objects.create(
                    degree_name=qualification,
                    degree_type="Permanent",
                    specialization=education_data.get("specialization", ""),
                )

            now = datetime.now().date()
            years_ago_start = education_data.get("years_ago_start", 6)
            years_ago_end = education_data.get("years_ago_end", 2)

            edu = EducationDetails.objects.create(
                institute=institute,
                degree=degree,
                from_date=now - timedelta(days=int(years_ago_start * 365)),
                to_date=now - timedelta(days=int(years_ago_end * 365)),
                score=education_data.get("score", ""),
                current_education=False,
            )
            user.education.set([edu])

    def _create_jobseeker_languages(self, user, languages_data):
        """Create language skills for the jobseeker."""
        # Clear existing languages first
        user.language.clear()

        lang_skills = []
        for lang_info in languages_data:
            lang_name = lang_info if isinstance(lang_info, str) else lang_info.get("name")
            language = Language.objects.filter(name__iexact=lang_name).first()
            if language:
                read = lang_info.get("read", True) if isinstance(lang_info, dict) else True
                write = lang_info.get("write", True) if isinstance(lang_info, dict) else True
                speak = lang_info.get("speak", True) if isinstance(lang_info, dict) else True

                user_lang = UserLanguage.objects.create(
                    language=language,
                    read=read,
                    write=write,
                    speak=speak,
                )
                lang_skills.append(user_lang)

        if lang_skills:
            user.language.set(lang_skills)
