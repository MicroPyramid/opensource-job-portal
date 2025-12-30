"""
Script to load test job data for development
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from peeldb.models import (
    JobPost, Company, City, Skill, Industry, Qualification,
    Country, State
)

User = get_user_model()


def get_or_create_company():
    """Get or create a test company and recruiter"""
    # Get or create a recruiter user
    recruiter, created = User.objects.get_or_create(
        email='recruiter@test.com',
        defaults={
            'username': 'testrecruiter',
            'user_type': 'RR',
            'is_active': True,
        }
    )
    if created:
        recruiter.set_password('testpass123')
        recruiter.save()
        print("Created test recruiter: recruiter@test.com")

    # Get or create a company
    company, created = Company.objects.get_or_create(
        name='Test Tech Company',
        defaults={
            'slug': 'test-tech-company',
            'company_type': 'Company',
            'is_active': True,
            'profile': 'A leading technology company specializing in software development.',
            'address': '123 Tech Park, Bangalore',
            'website': 'https://testtech.com',
            'phone_number': '9876543210',
        }
    )
    if created:
        print("Created test company: Test Tech Company")

    return company, recruiter


def load_test_jobs():
    """Load test job data"""

    company, recruiter = get_or_create_company()

    # Get some cities
    cities = list(City.objects.filter(status='Enabled')[:10])
    if not cities:
        print("No cities found. Please load cities fixture first.")
        print("Run: python manage.py loaddata cities.json")
        return

    # Get some skills
    skills = list(Skill.objects.filter(status='Active')[:20])
    if not skills:
        print("No skills found. Please run load_skills_data.py first.")
        return

    # Get or create industries
    industries_data = [
        {'name': 'IT-Software', 'slug': 'it-software'},
        {'name': 'BPO', 'slug': 'bpo'},
        {'name': 'Banking', 'slug': 'banking'},
        {'name': 'Education', 'slug': 'education'},
        {'name': 'Healthcare', 'slug': 'healthcare'},
        {'name': 'E-Commerce', 'slug': 'e-commerce'},
        {'name': 'Manufacturing', 'slug': 'manufacturing'},
        {'name': 'Consulting', 'slug': 'consulting'},
    ]
    industries = []
    for ind_data in industries_data:
        # Check if industry exists first (handle duplicates)
        ind = Industry.objects.filter(slug=ind_data['slug']).first()
        if not ind:
            ind = Industry.objects.filter(name__iexact=ind_data['name']).first()
        if not ind:
            ind = Industry.objects.create(
                name=ind_data['name'],
                slug=ind_data['slug'],
                status='Active'
            )
        industries.append(ind)

    # Get qualifications
    qualifications = list(Qualification.objects.filter(status='Active')[:5])

    # Job templates
    job_templates = [
        {
            'title': 'Python Developer',
            'job_role': 'Software Developer',
            'description': '''We are looking for a skilled Python Developer to join our team.

Responsibilities:
- Design and develop Python applications
- Write clean, maintainable code
- Collaborate with cross-functional teams
- Participate in code reviews

Requirements:
- 2+ years of Python experience
- Knowledge of Django or Flask
- Understanding of databases (PostgreSQL, MySQL)
- Strong problem-solving skills''',
            'min_salary': 500000,
            'max_salary': 1200000,
            'min_experience': 2,
            'max_experience': 5,
            'job_type': 'full-time',
        },
        {
            'title': 'Java Developer',
            'job_role': 'Software Developer',
            'description': '''Looking for experienced Java Developer.

Responsibilities:
- Develop Java-based applications
- Maintain and improve existing codebase
- Work with Spring Boot framework

Requirements:
- 3+ years Java experience
- Spring Boot knowledge
- Microservices architecture''',
            'min_salary': 600000,
            'max_salary': 1500000,
            'min_experience': 3,
            'max_experience': 7,
            'job_type': 'full-time',
        },
        {
            'title': 'React Developer',
            'job_role': 'Frontend Developer',
            'description': '''Join our frontend team as a React Developer.

Responsibilities:
- Build responsive web applications
- Implement UI components
- Optimize application performance

Requirements:
- 2+ years React experience
- TypeScript knowledge
- CSS/SASS expertise''',
            'min_salary': 400000,
            'max_salary': 1000000,
            'min_experience': 2,
            'max_experience': 5,
            'job_type': 'full-time',
        },
        {
            'title': 'DevOps Engineer',
            'job_role': 'DevOps Engineer',
            'description': '''We need a DevOps Engineer to manage our infrastructure.

Responsibilities:
- Manage CI/CD pipelines
- Handle cloud infrastructure (AWS/Azure)
- Implement monitoring solutions

Requirements:
- 3+ years DevOps experience
- Docker and Kubernetes
- AWS or Azure certification preferred''',
            'min_salary': 800000,
            'max_salary': 2000000,
            'min_experience': 3,
            'max_experience': 8,
            'job_type': 'full-time',
        },
        {
            'title': 'Data Analyst Intern',
            'job_role': 'Data Analyst',
            'description': '''Internship opportunity for aspiring Data Analysts.

Responsibilities:
- Analyze data sets
- Create reports and visualizations
- Support senior analysts

Requirements:
- Pursuing degree in related field
- Basic SQL knowledge
- Excel proficiency''',
            'min_salary': 100000,
            'max_salary': 200000,
            'min_experience': 0,
            'max_experience': 1,
            'job_type': 'internship',
        },
        {
            'title': 'Full Stack Developer',
            'job_role': 'Full Stack Developer',
            'description': '''Looking for Full Stack Developer with modern tech stack.

Responsibilities:
- Build end-to-end features
- Work with React and Node.js
- Database design and optimization

Requirements:
- 4+ years full stack experience
- React, Node.js, PostgreSQL
- REST API design''',
            'min_salary': 1000000,
            'max_salary': 2500000,
            'min_experience': 4,
            'max_experience': 10,
            'job_type': 'full-time',
        },
        {
            'title': 'Software Engineer - Fresher',
            'job_role': 'Software Engineer',
            'description': '''Entry level position for fresh graduates.

Responsibilities:
- Learn and contribute to projects
- Write code under supervision
- Participate in team activities

Requirements:
- B.Tech/B.E in Computer Science
- Basic programming knowledge
- Good communication skills''',
            'min_salary': 300000,
            'max_salary': 500000,
            'min_experience': 0,
            'max_experience': 1,
            'job_type': 'full-time',
            'is_fresher': True,
        },
        {
            'title': 'Remote Python Developer',
            'job_role': 'Software Developer',
            'description': '''100% Remote Python Developer position.

Responsibilities:
- Work remotely on Python projects
- Collaborate via online tools
- Deliver quality code

Requirements:
- 3+ years Python
- Self-motivated
- Good internet connection''',
            'min_salary': 800000,
            'max_salary': 1800000,
            'min_experience': 3,
            'max_experience': 7,
            'job_type': 'full-time',
            'is_remote': True,
        },
    ]

    created_count = 0

    for i, template in enumerate(job_templates):
        # Create multiple variations of each job
        for j in range(3):  # 3 jobs per template = 24 jobs total
            city = random.choice(cities)
            industry = random.choice(industries)
            job_skills = random.sample(skills, min(5, len(skills)))

            title = template['title']
            if j > 0:
                title = f"{title} - {city.name}"

            # Check if job already exists
            existing = JobPost.objects.filter(
                title=title,
                company=company
            ).first()

            if existing:
                continue

            job = JobPost.objects.create(
                title=title,
                slug=f"/{title.lower().replace(' ', '-')}-{i}-{j}/",
                job_role=template['job_role'],
                description=template['description'],
                company=company,
                user=recruiter,
                status='Live',
                min_salary=template['min_salary'],
                max_salary=template['max_salary'],
                min_year=template['min_experience'],
                max_year=template['max_experience'],
                min_month=0,
                max_month=0,
                job_type=template['job_type'],
                vacancies=random.randint(1, 10),
                published_on=datetime.now() - timedelta(days=random.randint(1, 30)),
                fresher=template.get('is_fresher', False),
                meta_title=f"{title} - Job Opening",
                meta_description=f"Apply for {title} position at Test Tech Company.",
            )

            # Add relationships
            job.location.add(city)
            job.skills.add(*job_skills)
            job.industry.add(industry)
            if qualifications:
                job.edu_qualification.add(random.choice(qualifications))

            if template.get('is_fresher'):
                job.min_experience = 0
                job.max_experience = 1
                job.save()

            created_count += 1

    total_jobs = JobPost.objects.filter(status='Live').count()
    print(f"Created {created_count} new jobs")
    print(f"Total live jobs in database: {total_jobs}")


if __name__ == "__main__":
    print("Loading test job data...")
    print("-" * 50)
    load_test_jobs()
    print("-" * 50)
    print("Done!")

