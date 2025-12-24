"""
Management command to create comprehensive test data for the job portal.

Usage:
    python manage.py create_test_data
    python manage.py create_test_data --clear
    python manage.py create_test_data --companies=100 --jobs=2000
"""
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from peeldb.models import (
    Company, User, JobPost, AppliedJobs, City, State, Country,
    Skill, Industry, Qualification, Language,
    TechnicalSkill, EmploymentHistory, EducationDetails,
    EducationInstitue, Degree, UserLanguage, InterviewLocation,
)

from .test_data.indian_names import (
    INDIAN_FIRST_NAMES, INDIAN_FIRST_NAMES_MALE, INDIAN_FIRST_NAMES_FEMALE,
    INDIAN_LAST_NAMES, INDIAN_UNIVERSITIES, INDIAN_COLLEGES,
)
from .test_data.company_names import (
    COMPANY_PREFIXES, COMPANY_SUFFIXES, COMPANY_TYPE_SUFFIXES,
    BUSINESS_PARKS, BUILDINGS, AREAS, COMPANY_PROFILES,
)
from .test_data.job_titles import (
    JOB_TITLES_BY_SKILL, DEFAULT_JOB_TITLES, JOB_DESCRIPTION_TEMPLATES,
    RECRUITER_TITLES,
)
from .test_data.constants import (
    COMPANY_SIZES, COMPANY_TYPES, USER_TYPE_JOBSEEKER, USER_TYPE_EMPLOYER,
    GENDERS, JOB_TYPES, COMMON_JOB_TYPES, WORK_MODES, JOB_POST_STATUSES,
    COMMON_JOB_STATUSES, JOB_STATUS_WEIGHTS, APPLICATION_STATUSES,
    APPLICATION_STATUS_WEIGHTS, SENIORITY_LEVELS, SKILL_PROFICIENCIES,
    SKILL_PROFICIENCY_WEIGHTS, NOTICE_PERIODS, SALARY_RANGES,
    TEST_DATA_MARKER, TEST_PASSWORD, BATCH_SIZE,
)


class Command(BaseCommand):
    help = "Creates comprehensive test data for the job portal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._used_emails = set()
        self._used_company_names = set()
        self._used_slugs = set()

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )
        parser.add_argument(
            '--companies',
            type=int,
            default=50,
            help='Number of companies to create (default: 50)',
        )
        parser.add_argument(
            '--recruiters',
            type=int,
            default=100,
            help='Number of recruiters to create (default: 100)',
        )
        parser.add_argument(
            '--jobseekers',
            type=int,
            default=500,
            help='Number of job seekers to create (default: 500)',
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=1000,
            help='Number of jobs to create (default: 1000)',
        )
        parser.add_argument(
            '--applications',
            type=int,
            default=3000,
            help='Number of job applications to create (default: 3000)',
        )

    def handle(self, *args, **options):
        # Disable Haystack signals during data creation
        signal_processor = apps.get_app_config("haystack").signal_processor
        signal_processor.teardown()

        try:
            if options['clear']:
                self._clear_test_data()

            self._validate_fixtures_loaded()

            # Load reference data
            self.cities = list(City.objects.filter(status="Enabled"))
            self.skills = list(Skill.objects.filter(status="Active"))
            self.industries = list(Industry.objects.filter(status="Active"))
            self.qualifications = list(Qualification.objects.all())
            self.languages = list(Language.objects.all())
            self.country = Country.objects.filter(status="Enabled").first()

            with transaction.atomic():
                # Create education infrastructure first
                self._create_education_infrastructure()

                # Create main entities
                companies = self._create_companies(options['companies'])
                recruiters = self._create_recruiters(options['recruiters'], companies)
                job_seekers = self._create_job_seekers(options['jobseekers'])
                jobs = self._create_jobs(options['jobs'], recruiters, companies)
                self._create_applications(options['applications'], jobs, job_seekers)

            self.stdout.write(self.style.SUCCESS(
                f"\nSuccessfully created test data:\n"
                f"  - {len(companies)} companies\n"
                f"  - {len(recruiters)} recruiters\n"
                f"  - {len(job_seekers)} job seekers\n"
                f"  - {len(jobs)} jobs\n"
                f"  - {options['applications']} applications"
            ))
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

    def _clear_test_data(self):
        """Clear all test data (preserves fixture data)."""
        self.stdout.write("Clearing existing test data...")

        # Clear in reverse order of dependencies
        AppliedJobs.objects.filter(
            job_post__meta_description__contains=TEST_DATA_MARKER
        ).delete()
        JobPost.objects.filter(meta_description__contains=TEST_DATA_MARKER).delete()
        User.objects.filter(profile_description__contains=TEST_DATA_MARKER).delete()
        Company.objects.filter(profile__contains=TEST_DATA_MARKER).delete()

        # Clean up orphaned records
        EmploymentHistory.objects.filter(user__isnull=True).delete()
        TechnicalSkill.objects.filter(user__isnull=True).delete()
        EducationDetails.objects.filter(user__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS("Test data cleared."))

    def _create_education_infrastructure(self):
        """Create education institutes and degrees if not enough exist."""
        # Create institutes
        existing_institutes = EducationInstitue.objects.count()
        if existing_institutes < 50:
            self.stdout.write("Creating education institutes...")
            for city in random.sample(self.cities, min(30, len(self.cities))):
                for template in INDIAN_UNIVERSITIES[:5]:
                    name = f"{template} {city.name}"
                    if not EducationInstitue.objects.filter(name=name).exists():
                        EducationInstitue.objects.create(
                            name=name,
                            address=f"{city.name}, {city.state.name}",
                            city=city
                        )
                for template in INDIAN_COLLEGES[:3]:
                    name = f"{template} {city.name}"
                    if not EducationInstitue.objects.filter(name=name).exists():
                        EducationInstitue.objects.create(
                            name=name,
                            address=f"{city.name}, {city.state.name}",
                            city=city
                        )

        self.institutes = list(EducationInstitue.objects.all())

    def _generate_unique_email(self, first_name, last_name, domain_hint):
        """Generate a unique email address."""
        base = f"{first_name.lower()}.{last_name.lower()}"
        counter = 0
        while True:
            suffix = f"{counter}" if counter > 0 else ""
            email = f"{base}{suffix}@{domain_hint.replace(' ', '').lower()}.test"
            username = email.split("@")[0]
            # Check both in-memory set and database
            if email not in self._used_emails and not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                self._used_emails.add(email)
                return email
            counter += 1

    def _generate_unique_slug(self, name, prefix=""):
        """Generate a unique slug."""
        base_slug = slugify(f"{prefix}-{name}" if prefix else name)
        slug = base_slug
        counter = 0
        while slug in self._used_slugs:
            counter += 1
            slug = f"{base_slug}-{counter}"
        self._used_slugs.add(slug)
        return slug

    def _generate_company_name(self):
        """Generate a unique realistic company name."""
        patterns = [
            lambda: f"{random.choice(COMPANY_PREFIXES)}{random.choice(COMPANY_SUFFIXES)}",
            lambda: f"{random.choice(INDIAN_LAST_NAMES)} {random.choice(COMPANY_SUFFIXES)}",
            lambda: f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)} {random.choice(COMPANY_TYPE_SUFFIXES)}",
            lambda: f"{random.choice(COMPANY_PREFIXES)}{random.choice(COMPANY_SUFFIXES)} India",
        ]

        while True:
            name = random.choice(patterns)()
            if name not in self._used_company_names and not Company.objects.filter(name=name).exists():
                self._used_company_names.add(name)
                return name

    def _create_companies(self, count):
        """Create companies with progress output."""
        self.stdout.write(f"Creating {count} companies...")

        companies = []
        for i in range(count):
            if (i + 1) % 10 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} companies...")

            city = random.choice(self.cities)
            name = self._generate_company_name()
            slug = self._generate_unique_slug(name)

            company = Company.objects.create(
                name=name,
                slug=slug,
                website=f"https://www.{slugify(name).replace('-', '')}.com",
                address=f"{random.randint(1, 500)}, {random.choice(BUSINESS_PARKS)}, {city.name}",
                profile=f"<p>{name} is a leading technology company. {random.choice(COMPANY_PROFILES)} {TEST_DATA_MARKER}</p>",
                phone_number=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"hr@{slugify(name).replace('-', '')}.com",
                size=random.choice(COMPANY_SIZES),
                company_type=random.choice(COMPANY_TYPES),
                is_active=True,
            )
            companies.append(company)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(companies)} companies."))
        return companies

    def _create_recruiters(self, count, companies):
        """Create recruiters linked to companies."""
        self.stdout.write(f"Creating {count} recruiters...")

        recruiters = []
        company_admin_created = set()

        for i in range(count):
            if (i + 1) % 20 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} recruiters...")

            company = random.choice(companies)
            city = random.choice(self.cities)
            first_name = random.choice(INDIAN_FIRST_NAMES)
            last_name = random.choice(INDIAN_LAST_NAMES)
            email = self._generate_unique_email(first_name, last_name, company.slug)

            # First recruiter for each company is admin
            is_admin = company.id not in company_admin_created
            if is_admin:
                company_admin_created.add(company.id)

            user = User.objects.create(
                username=email.split("@")[0],
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=USER_TYPE_EMPLOYER,
                company=company,
                is_active=True,
                is_admin=is_admin,
                mobile_verified=True,
                email_verified=True,
                city=city,
                state=city.state,
                country=city.state.country,
                mobile=f"+91{random.randint(7000000000, 9999999999)}",
                profile_description=f"Recruiter at {company.name}. {TEST_DATA_MARKER}",
                job_title=random.choice(RECRUITER_TITLES),
            )
            user.set_password(TEST_PASSWORD)
            user.save()

            # Add industries and skills
            user.industry.set(random.sample(self.industries, min(3, len(self.industries))))
            user.technical_skills.set(random.sample(self.skills, min(5, len(self.skills))))

            recruiters.append(user)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(recruiters)} recruiters."))
        return recruiters

    def _create_job_seekers(self, count):
        """Create job seekers with complete profiles."""
        self.stdout.write(f"Creating {count} job seekers...")

        job_seekers = []

        for i in range(count):
            if (i + 1) % 50 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} job seekers...")

            city = random.choice(self.cities)
            gender = random.choice(GENDERS)
            first_names = INDIAN_FIRST_NAMES_MALE if gender == "M" else INDIAN_FIRST_NAMES_FEMALE
            first_name = random.choice(first_names)
            last_name = random.choice(INDIAN_LAST_NAMES)
            email = self._generate_unique_email(first_name, last_name, "jobseeker")

            years_exp = random.randint(0, 15)
            months_exp = random.randint(0, 11)

            # Calculate salary based on experience
            salary_key = max(k for k in SALARY_RANGES.keys() if k <= years_exp)
            min_sal, max_sal = SALARY_RANGES[salary_key]
            current_salary = random.randint(min_sal, max_sal)
            expected_salary = int(current_salary * random.uniform(1.1, 1.4))

            # Generate DOB based on experience
            age = 22 + years_exp + random.randint(0, 5)
            dob = (datetime.now() - timedelta(days=age * 365 + random.randint(0, 364))).date()

            user = User.objects.create(
                username=email.split("@")[0],
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=USER_TYPE_JOBSEEKER,
                is_active=True,
                mobile_verified=random.choice([True, False]),
                email_verified=random.choice([True, False]),
                city=city,
                current_city=city,
                state=city.state,
                country=city.state.country,
                mobile=f"+91{random.randint(7000000000, 9999999999)}",
                year=str(years_exp),
                month=str(months_exp),
                current_salary=str(current_salary),
                expected_salary=str(expected_salary),
                dob=dob,
                gender=gender,
                profile_description=f"Experienced professional with {years_exp} years in IT. {TEST_DATA_MARKER}",
                resume_title=f"{first_name} {last_name} - Resume",
                is_looking_for_job=random.choice([True, False]),
                is_open_to_offers=random.choice([True, False]),
                relocation=random.choice([True, False]),
                notice_period=random.choice(NOTICE_PERIODS),
            )
            user.set_password(TEST_PASSWORD)
            user.save()

            # Add preferred cities
            user.preferred_city.set(random.sample(self.cities, min(3, len(self.cities))))

            # Create technical skills
            self._create_user_skills(user, years_exp)

            # Create employment history
            self._create_employment_history(user, years_exp)

            # Create education details
            self._create_education_details(user)

            # Create language skills
            self._create_language_skills(user)

            job_seekers.append(user)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(job_seekers)} job seekers."))
        return job_seekers

    def _create_user_skills(self, user, years_exp):
        """Create technical skills for a user."""
        num_skills = random.randint(3, 7)
        selected_skills = random.sample(self.skills, min(num_skills, len(self.skills)))

        tech_skills = []
        for i, skill in enumerate(selected_skills):
            proficiency = random.choices(
                SKILL_PROFICIENCIES,
                weights=SKILL_PROFICIENCY_WEIGHTS
            )[0]

            tech_skill = TechnicalSkill.objects.create(
                skill=skill,
                year=min(years_exp, random.randint(1, years_exp + 1)) if years_exp > 0 else 0,
                month=random.randint(0, 11),
                proficiency=proficiency,
                is_major=(i == 0),  # First skill is major
            )
            tech_skills.append(tech_skill)

        user.skills.set(tech_skills)

    def _create_employment_history(self, user, years_exp):
        """Create employment history for a user."""
        if years_exp == 0:
            return

        num_jobs = min(years_exp // 2 + 1, 4)
        history = []

        current_date = datetime.now().date()
        for j in range(num_jobs):
            is_current = (j == 0)
            job_duration = random.randint(12, 36)  # months

            to_date = current_date if is_current else (current_date - timedelta(days=random.randint(30, 180)))
            from_date = to_date - timedelta(days=job_duration * 30)
            current_date = from_date - timedelta(days=random.randint(30, 90))

            emp = EmploymentHistory.objects.create(
                company=self._generate_company_name(),
                designation=random.choice([
                    "Software Engineer", "Senior Developer", "Team Lead",
                    "Technical Architect", "Project Manager", "Associate",
                ]),
                from_date=from_date,
                to_date=None if is_current else to_date,
                current_job=is_current,
                job_profile=f"Worked on various software development projects.",
            )
            history.append(emp)

        user.employment_history.set(history)

    def _create_education_details(self, user):
        """Create education details for a user."""
        if not self.institutes or not self.qualifications:
            return

        education = []
        num_degrees = random.randint(1, 2)

        for _ in range(num_degrees):
            institute = random.choice(self.institutes)
            qualification = random.choice(self.qualifications)

            # Create degree if not exists
            degree, _ = Degree.objects.get_or_create(
                degree_name=qualification,
                defaults={
                    "degree_type": "Permanent",
                    "specialization": random.choice([
                        "Computer Science", "Information Technology",
                        "Electronics", "Mechanical", "Civil",
                    ]),
                }
            )

            to_date = datetime.now().date() - timedelta(days=random.randint(365, 3650))
            from_date = to_date - timedelta(days=random.randint(730, 1460))

            edu = EducationDetails.objects.create(
                institute=institute,
                degree=degree,
                from_date=from_date,
                to_date=to_date,
                score=f"{random.randint(60, 95)}%",
                current_education=False,
            )
            education.append(edu)

        user.education.set(education)

    def _create_language_skills(self, user):
        """Create language skills for a user."""
        if not self.languages:
            return

        num_languages = random.randint(1, 3)
        selected_languages = random.sample(self.languages, min(num_languages, len(self.languages)))

        lang_skills = []
        for lang in selected_languages:
            user_lang = UserLanguage.objects.create(
                language=lang,
                read=random.choice([True, True, True, False]),
                write=random.choice([True, True, False, False]),
                speak=random.choice([True, True, True, False]),
            )
            lang_skills.append(user_lang)

        user.language.set(lang_skills)

    def _create_jobs(self, count, recruiters, companies):
        """Create job posts."""
        self.stdout.write(f"Creating {count} jobs...")

        jobs = []

        for i in range(count):
            if (i + 1) % 100 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} jobs...")

            recruiter = random.choice(recruiters)
            company = recruiter.company or random.choice(companies)
            primary_skill = random.choice(self.skills)

            # Get job title for this skill
            skill_slug = primary_skill.slug.replace("-", "_")
            titles = JOB_TITLES_BY_SKILL.get(skill_slug)
            if titles:
                title = random.choice(titles)
            else:
                title = random.choice(DEFAULT_JOB_TITLES).format(skill=primary_skill.name)

            # Experience range
            min_year = random.choice([0, 1, 2, 3, 5, 7])
            max_year = min_year + random.randint(2, 5)

            # Salary based on experience
            salary_key = max(k for k in SALARY_RANGES.keys() if k <= min_year)
            min_sal, max_sal = SALARY_RANGES[salary_key]
            min_salary = random.randint(min_sal, (min_sal + max_sal) // 2)
            max_salary = random.randint((min_sal + max_sal) // 2, max_sal)

            job_type = random.choice(COMMON_JOB_TYPES)
            status = random.choices(COMMON_JOB_STATUSES, weights=JOB_STATUS_WEIGHTS)[0]

            city = random.choice(self.cities)

            # Generate description
            description = random.choice(JOB_DESCRIPTION_TEMPLATES).format(
                title=title,
                company=company.name,
                city=city.name,
                primary_skill=primary_skill.name,
                min_exp=min_year,
                max_exp=max_year,
            )

            slug = self._generate_unique_slug(title, prefix=str(i))

            job = JobPost.objects.create(
                user=recruiter,
                company=company,
                title=title,
                slug=slug,
                description=description,
                vacancies=random.randint(1, 10),
                min_year=min_year,
                max_year=max_year,
                min_month=0,
                max_month=0,
                min_salary=min_salary,
                max_salary=max_salary,
                salary_type="Year",
                job_type=job_type,
                work_mode=random.choice(WORK_MODES),
                status=status,
                published_on=timezone.now() - timedelta(days=random.randint(0, 60)),
                meta_title=f"{title} Jobs - {company.name}",
                meta_description=f"Apply for {title} position at {company.name}. {TEST_DATA_MARKER}",
                fresher=(min_year == 0),
                company_name=company.name,
                company_address=company.address,
                company_description=company.profile,
                country=self.country,
                seniority_level=random.choice(SENIORITY_LEVELS),
            )

            # Add M2M relations
            job.location.set(random.sample(self.cities, min(random.randint(1, 3), len(self.cities))))
            job.skills.set([primary_skill] + random.sample(self.skills, min(random.randint(1, 4), len(self.skills))))
            job.industry.set(random.sample(self.industries, min(random.randint(1, 2), len(self.industries))))
            if self.qualifications:
                job.edu_qualification.set(random.sample(self.qualifications, min(random.randint(1, 2), len(self.qualifications))))

            jobs.append(job)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(jobs)} jobs."))
        return jobs

    def _create_applications(self, count, jobs, job_seekers):
        """Create job applications."""
        self.stdout.write(f"Creating {count} applications...")

        # Filter only live jobs for applications
        live_jobs = [j for j in jobs if j.status == "Live"]
        if not live_jobs:
            live_jobs = jobs[:len(jobs)//2]  # Use half if no live jobs

        applications_created = 0
        existing_applications = set()

        for i in range(count):
            if (i + 1) % 500 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} applications...")

            job = random.choice(live_jobs)
            job_seeker = random.choice(job_seekers)

            # Avoid duplicate applications
            key = (job.id, job_seeker.id)
            if key in existing_applications:
                continue
            existing_applications.add(key)

            status = random.choices(
                APPLICATION_STATUSES,
                weights=APPLICATION_STATUS_WEIGHTS
            )[0]

            AppliedJobs.objects.create(
                job_post=job,
                user=job_seeker,
                status=status,
                ip_address="127.0.0.1",
                user_agent="Test Data Generator",
            )
            applications_created += 1

        self.stdout.write(self.style.SUCCESS(f"  Created {applications_created} applications."))
