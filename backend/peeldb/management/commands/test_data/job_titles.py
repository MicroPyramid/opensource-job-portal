# Job titles and description templates

# Job titles mapped by skill slug
JOB_TITLES_BY_SKILL = {
    "java": [
        "Java Developer", "Senior Java Developer", "Java Full Stack Developer",
        "Java Backend Engineer", "Java Technical Lead", "Java Architect",
        "Java Software Engineer", "Core Java Developer", "Java Spring Developer",
    ],
    "dot-net": [
        ".NET Developer", "Senior .NET Developer", ".NET Full Stack Developer",
        "C# Developer", "ASP.NET Developer", ".NET Core Developer",
        ".NET Technical Lead", "Microsoft .NET Engineer",
    ],
    "python": [
        "Python Developer", "Senior Python Engineer", "Python Backend Developer",
        "Django Developer", "Flask Developer", "Python Full Stack Developer",
        "Data Engineer - Python", "Python Automation Engineer",
    ],
    "php": [
        "PHP Developer", "Senior PHP Developer", "Laravel Developer",
        "PHP Full Stack Developer", "WordPress Developer", "Drupal Developer",
        "PHP Backend Engineer", "CodeIgniter Developer",
    ],
    "c": [
        "C Developer", "Embedded C Developer", "Systems Programmer",
        "C/C++ Developer", "Firmware Developer", "Embedded Software Engineer",
    ],
    "javascript": [
        "JavaScript Developer", "Frontend Developer", "Full Stack JavaScript Developer",
        "Node.js Developer", "React Developer", "Angular Developer",
        "Vue.js Developer", "Senior Frontend Engineer",
    ],
    "react": [
        "React Developer", "Senior React Developer", "React.js Engineer",
        "React Native Developer", "Frontend Developer - React",
        "React Full Stack Developer", "React UI Developer",
    ],
    "angular": [
        "Angular Developer", "Senior Angular Developer", "Angular Frontend Engineer",
        "Angular Full Stack Developer", "UI Developer - Angular",
    ],
    "nodejs": [
        "Node.js Developer", "Backend Developer - Node.js", "Senior Node.js Engineer",
        "Node.js Full Stack Developer", "Express.js Developer",
    ],
    "aws": [
        "AWS Solutions Architect", "AWS DevOps Engineer", "Cloud Engineer - AWS",
        "AWS Administrator", "Senior AWS Developer", "AWS Infrastructure Engineer",
    ],
    "devops": [
        "DevOps Engineer", "Senior DevOps Engineer", "Site Reliability Engineer",
        "DevOps Architect", "Platform Engineer", "Infrastructure Engineer",
    ],
    "data-science": [
        "Data Scientist", "Senior Data Scientist", "Machine Learning Engineer",
        "AI/ML Engineer", "Data Analyst", "Research Scientist",
    ],
    "sql": [
        "SQL Developer", "Database Developer", "Database Administrator",
        "SQL Server DBA", "Data Engineer", "BI Developer",
    ],
    "android": [
        "Android Developer", "Senior Android Developer", "Android Engineer",
        "Mobile Developer - Android", "Android Team Lead",
    ],
    "ios": [
        "iOS Developer", "Senior iOS Developer", "Swift Developer",
        "Mobile Developer - iOS", "iOS Engineer",
    ],
    "testing": [
        "QA Engineer", "Senior QA Engineer", "Test Automation Engineer",
        "SDET", "Quality Analyst", "Manual Tester", "Performance Tester",
    ],
    "selenium": [
        "Selenium Automation Engineer", "Test Automation Engineer",
        "QA Automation Engineer", "Selenium Tester", "Automation Test Lead",
    ],
}

# Default titles for skills not in the mapping
DEFAULT_JOB_TITLES = [
    "{skill} Developer", "Senior {skill} Developer", "{skill} Engineer",
    "{skill} Specialist", "Software Engineer - {skill}", "{skill} Consultant",
]

# Job description templates
JOB_DESCRIPTION_TEMPLATES = [
    """<p>We are looking for a talented <strong>{title}</strong> to join our team in {city}.</p>

<h3>Requirements:</h3>
<ul>
<li>{min_exp}-{max_exp} years of experience in {primary_skill}</li>
<li>Strong problem-solving and analytical skills</li>
<li>Excellent communication skills</li>
<li>Bachelor's degree in Computer Science or related field</li>
</ul>

<h3>What we offer:</h3>
<ul>
<li>Competitive salary and benefits</li>
<li>Health insurance</li>
<li>Flexible working hours</li>
<li>Learning and development opportunities</li>
</ul>""",

    """<p><strong>{company}</strong> is hiring a <strong>{title}</strong> for our {city} office.</p>

<h3>Job Description:</h3>
<p>As a {title}, you will be responsible for designing, developing, and maintaining software applications using {primary_skill} and related technologies.</p>

<h3>Required Skills:</h3>
<ul>
<li>{min_exp}+ years of hands-on experience with {primary_skill}</li>
<li>Experience with agile development methodologies</li>
<li>Strong debugging and troubleshooting skills</li>
</ul>

<h3>Benefits:</h3>
<ul>
<li>Competitive compensation package</li>
<li>Work-life balance</li>
<li>Career growth opportunities</li>
</ul>""",

    """<h2>{title} - {company}</h2>

<p>Join our growing team as a {title} and work on exciting projects!</p>

<h3>Responsibilities:</h3>
<ul>
<li>Design and implement scalable solutions</li>
<li>Write clean, maintainable code</li>
<li>Collaborate with cross-functional teams</li>
<li>Participate in code reviews</li>
</ul>

<h3>Qualifications:</h3>
<ul>
<li>{min_exp}-{max_exp} years of relevant experience</li>
<li>Proficiency in {primary_skill}</li>
<li>BE/BTech/MCA or equivalent</li>
</ul>

<h3>Location:</h3>
<p>{city}</p>""",
]

# Recruiter job titles
RECRUITER_TITLES = [
    "HR Manager", "Senior Recruiter", "Talent Acquisition Lead",
    "HR Executive", "Recruitment Specialist", "Technical Recruiter",
    "HR Business Partner", "Talent Acquisition Specialist",
    "Recruitment Manager", "HR Coordinator", "Sourcing Specialist",
]

# Experience level descriptions
EXPERIENCE_LEVELS = {
    0: "Fresher",
    1: "Entry Level",
    2: "Junior",
    3: "Mid-Level",
    5: "Senior",
    8: "Lead",
    10: "Principal",
    12: "Architect",
}
