"""
Script to load skills data directly into the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from peeldb.models import Skill

def load_skills():
    """Load common skill data"""
    skills_data = [
        # Programming Languages
        {"name": "Python", "slug": "python", "skill_type": "it", "status": "Active"},
        {"name": "Java", "slug": "java", "skill_type": "it", "status": "Active"},
        {"name": "JavaScript", "slug": "javascript", "skill_type": "it", "status": "Active"},
        {"name": "TypeScript", "slug": "typescript", "skill_type": "it", "status": "Active"},
        {"name": "C++", "slug": "cpp", "skill_type": "it", "status": "Active"},
        {"name": "C#", "slug": "csharp", "skill_type": "it", "status": "Active"},
        {"name": "Go", "slug": "go", "skill_type": "it", "status": "Active"},
        {"name": "Rust", "slug": "rust", "skill_type": "it", "status": "Active"},
        {"name": "PHP", "slug": "php", "skill_type": "it", "status": "Active"},
        {"name": "Ruby", "slug": "ruby", "skill_type": "it", "status": "Active"},
        {"name": "Swift", "slug": "swift", "skill_type": "it", "status": "Active"},
        {"name": "Kotlin", "slug": "kotlin", "skill_type": "it", "status": "Active"},
        {"name": "Scala", "slug": "scala", "skill_type": "it", "status": "Active"},
        {"name": "R", "slug": "r-language", "skill_type": "it", "status": "Active"},

        # Web Frameworks
        {"name": "React", "slug": "react", "skill_type": "it", "status": "Active"},
        {"name": "Angular", "slug": "angular", "skill_type": "it", "status": "Active"},
        {"name": "Vue.js", "slug": "vuejs", "skill_type": "it", "status": "Active"},
        {"name": "Svelte", "slug": "svelte", "skill_type": "it", "status": "Active"},
        {"name": "Next.js", "slug": "nextjs", "skill_type": "it", "status": "Active"},
        {"name": "Node.js", "slug": "nodejs", "skill_type": "it", "status": "Active"},
        {"name": "Express.js", "slug": "expressjs", "skill_type": "it", "status": "Active"},
        {"name": "Django", "slug": "django", "skill_type": "it", "status": "Active"},
        {"name": "Flask", "slug": "flask", "skill_type": "it", "status": "Active"},
        {"name": "FastAPI", "slug": "fastapi", "skill_type": "it", "status": "Active"},
        {"name": "Spring Boot", "slug": "spring-boot", "skill_type": "it", "status": "Active"},
        {"name": "Ruby on Rails", "slug": "ruby-on-rails", "skill_type": "it", "status": "Active"},
        {"name": "Laravel", "slug": "laravel", "skill_type": "it", "status": "Active"},
        {"name": ".NET", "slug": "dotnet", "skill_type": "it", "status": "Active"},
        {"name": "ASP.NET", "slug": "aspnet", "skill_type": "it", "status": "Active"},

        # Databases
        {"name": "MySQL", "slug": "mysql", "skill_type": "it", "status": "Active"},
        {"name": "PostgreSQL", "slug": "postgresql", "skill_type": "it", "status": "Active"},
        {"name": "MongoDB", "slug": "mongodb", "skill_type": "it", "status": "Active"},
        {"name": "Redis", "slug": "redis", "skill_type": "it", "status": "Active"},
        {"name": "Elasticsearch", "slug": "elasticsearch", "skill_type": "it", "status": "Active"},
        {"name": "Oracle", "slug": "oracle", "skill_type": "it", "status": "Active"},
        {"name": "SQL Server", "slug": "sql-server", "skill_type": "it", "status": "Active"},
        {"name": "SQLite", "slug": "sqlite", "skill_type": "it", "status": "Active"},
        {"name": "Cassandra", "slug": "cassandra", "skill_type": "it", "status": "Active"},
        {"name": "DynamoDB", "slug": "dynamodb", "skill_type": "it", "status": "Active"},

        # Cloud & DevOps
        {"name": "AWS", "slug": "aws", "skill_type": "it", "status": "Active"},
        {"name": "Azure", "slug": "azure", "skill_type": "it", "status": "Active"},
        {"name": "Google Cloud", "slug": "google-cloud", "skill_type": "it", "status": "Active"},
        {"name": "Docker", "slug": "docker", "skill_type": "it", "status": "Active"},
        {"name": "Kubernetes", "slug": "kubernetes", "skill_type": "it", "status": "Active"},
        {"name": "Jenkins", "slug": "jenkins", "skill_type": "it", "status": "Active"},
        {"name": "Git", "slug": "git", "skill_type": "it", "status": "Active"},
        {"name": "GitHub", "slug": "github", "skill_type": "it", "status": "Active"},
        {"name": "GitLab", "slug": "gitlab", "skill_type": "it", "status": "Active"},
        {"name": "Terraform", "slug": "terraform", "skill_type": "it", "status": "Active"},
        {"name": "Ansible", "slug": "ansible", "skill_type": "it", "status": "Active"},
        {"name": "CI/CD", "slug": "cicd", "skill_type": "it", "status": "Active"},
        {"name": "Linux", "slug": "linux", "skill_type": "it", "status": "Active"},

        # Data Science & ML
        {"name": "Machine Learning", "slug": "machine-learning", "skill_type": "it", "status": "Active"},
        {"name": "Deep Learning", "slug": "deep-learning", "skill_type": "it", "status": "Active"},
        {"name": "TensorFlow", "slug": "tensorflow", "skill_type": "it", "status": "Active"},
        {"name": "PyTorch", "slug": "pytorch", "skill_type": "it", "status": "Active"},
        {"name": "Pandas", "slug": "pandas", "skill_type": "it", "status": "Active"},
        {"name": "NumPy", "slug": "numpy", "skill_type": "it", "status": "Active"},
        {"name": "Data Analysis", "slug": "data-analysis", "skill_type": "it", "status": "Active"},
        {"name": "Data Science", "slug": "data-science", "skill_type": "it", "status": "Active"},
        {"name": "NLP", "slug": "nlp", "skill_type": "it", "status": "Active"},
        {"name": "Computer Vision", "slug": "computer-vision", "skill_type": "it", "status": "Active"},

        # Mobile
        {"name": "Android", "slug": "android", "skill_type": "it", "status": "Active"},
        {"name": "iOS", "slug": "ios", "skill_type": "it", "status": "Active"},
        {"name": "React Native", "slug": "react-native", "skill_type": "it", "status": "Active"},
        {"name": "Flutter", "slug": "flutter", "skill_type": "it", "status": "Active"},

        # Frontend
        {"name": "HTML", "slug": "html", "skill_type": "it", "status": "Active"},
        {"name": "CSS", "slug": "css", "skill_type": "it", "status": "Active"},
        {"name": "Tailwind CSS", "slug": "tailwind-css", "skill_type": "it", "status": "Active"},
        {"name": "Bootstrap", "slug": "bootstrap", "skill_type": "it", "status": "Active"},
        {"name": "SASS", "slug": "sass", "skill_type": "it", "status": "Active"},
        {"name": "Webpack", "slug": "webpack", "skill_type": "it", "status": "Active"},

        # Testing
        {"name": "Selenium", "slug": "selenium", "skill_type": "it", "status": "Active"},
        {"name": "Jest", "slug": "jest", "skill_type": "it", "status": "Active"},
        {"name": "Pytest", "slug": "pytest", "skill_type": "it", "status": "Active"},
        {"name": "JUnit", "slug": "junit", "skill_type": "it", "status": "Active"},
        {"name": "Cypress", "slug": "cypress", "skill_type": "it", "status": "Active"},

        # Other IT Skills
        {"name": "REST API", "slug": "rest-api", "skill_type": "it", "status": "Active"},
        {"name": "GraphQL", "slug": "graphql", "skill_type": "it", "status": "Active"},
        {"name": "Microservices", "slug": "microservices", "skill_type": "it", "status": "Active"},
        {"name": "Agile", "slug": "agile", "skill_type": "it", "status": "Active"},
        {"name": "Scrum", "slug": "scrum", "skill_type": "it", "status": "Active"},
        {"name": "JIRA", "slug": "jira", "skill_type": "it", "status": "Active"},

        # Non-IT Skills
        {"name": "Communication", "slug": "communication", "skill_type": "non_it", "status": "Active"},
        {"name": "Leadership", "slug": "leadership", "skill_type": "non_it", "status": "Active"},
        {"name": "Problem Solving", "slug": "problem-solving", "skill_type": "non_it", "status": "Active"},
        {"name": "Team Management", "slug": "team-management", "skill_type": "non_it", "status": "Active"},
        {"name": "Project Management", "slug": "project-management", "skill_type": "non_it", "status": "Active"},
        {"name": "Time Management", "slug": "time-management", "skill_type": "non_it", "status": "Active"},
        {"name": "Critical Thinking", "slug": "critical-thinking", "skill_type": "non_it", "status": "Active"},
        {"name": "Presentation", "slug": "presentation", "skill_type": "non_it", "status": "Active"},
        {"name": "Negotiation", "slug": "negotiation", "skill_type": "non_it", "status": "Active"},
        {"name": "Sales", "slug": "sales", "skill_type": "non_it", "status": "Active"},
        {"name": "Marketing", "slug": "marketing", "skill_type": "non_it", "status": "Active"},
        {"name": "Customer Service", "slug": "customer-service", "skill_type": "non_it", "status": "Active"},
    ]

    created_count = 0
    for skill_data in skills_data:
        # Check if skill already exists (by slug or name)
        existing_skill = Skill.objects.filter(slug=skill_data["slug"]).first()
        if not existing_skill:
            existing_skill = Skill.objects.filter(name__iexact=skill_data["name"]).first()

        if not existing_skill:
            # Create new skill
            Skill.objects.create(
                name=skill_data["name"],
                slug=skill_data["slug"],
                skill_type=skill_data["skill_type"],
                status=skill_data["status"]
            )
            created_count += 1

    total_skills = Skill.objects.filter(status='Active').count()
    print(f"Loaded {len(skills_data)} skills ({created_count} new)")
    print(f"Total active skills in database: {total_skills}")


if __name__ == "__main__":
    print("Loading skills data...")
    print("-" * 50)
    load_skills()
    print("-" * 50)
    print("Done!")

