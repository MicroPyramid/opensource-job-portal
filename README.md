## Open Source Job Portal

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/105a3bf03bec4cfbac70d7c30e574bea)](https://www.codacy.com/manual/ashwin/opensource-job-portal?utm_source=github.com&utm_medium=referral&utm_content=MicroPyramid/opensource-job-portal&utm_campaign=Badge_Grade)  
[![Build Status](https://travis-ci.org/MicroPyramid/opensource-job-portal.svg?branch=master)](https://travis-ci.org/MicroPyramid/opensource-job-portal)  
[![Coverage Status](https://coveralls.io/repos/github/MicroPyramid/opensource-job-portal/badge.svg?branch=master)](https://coveralls.io/github/MicroPyramid/opensource-job-portal?branch=master)

A fully-featured, open-source job-posting portal built with Django, offering unlimited free job listings, social authentication, and seamless integrations.

🔗 **Documentation**  
Read the user guide and developer API docs on Read the Docs:  
https://opensource-job-portal.readthedocs.io/en/latest/

---

### Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
   - [Configuration](#configuration)  
   - [Database Setup & Data Seeding](#database-setup--data-seeding)  
   - [Running the App](#running-the-app)  
4. [Usage](#usage)  
5. [Contributing](#contributing)  
6. [License](#license)  

---

## Features

**For Recruiters**  
- Register via email/password **or** Google OAuth  
- Post, copy, deactivate, and manage job listings  
- Share jobs to Facebook, Twitter, and LinkedIn  
- Add “Walk-in” events with location via Google Maps integration  

**For Job Seekers / Portal Users**  
- Real-time job alerts by email  
- Responsive “new mobile” design  
- Keyword-based and advanced search filters  
- Save favorite jobs and application history  

**Under the Hood**  
- Full-text search powered by Elasticsearch  
- Asynchronous tasks via Redis + Celery  
- Caching with Memcached for blazingly fast page loads  
- RESTful JSON APIs for third-party integrations  

---

## Tech Stack

- **Backend**: Python 3.x, Django  
- **Frontend**: HTML5, CSS3, Bootstrap, Less/Sass  
- **Database**: PostgreSQL  
- **Search**: Elasticsearch  
- **Caching / Message Broker**: Redis, Memcached  
- **Containerization**: Docker  
- **CI/CD**: Travis CI, Coveralls  

---

## Getting Started

### Prerequisites

- Ubuntu 20.04 (or compatible Linux distro)  
- Python 3.8+ & `pip`  
- PostgreSQL  
- Node.js & `npm`  
- Docker & Docker Compose  
- Ruby & `gem` (for Sass)  

### Installation

1. **System packages**  
   ```bash
   sudo apt update
   sudo apt install -y git postgresql python3-dev python3-venv build-essential      redis-server memcached npm ruby-full
   ```
2. **Node.js & Less**  
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   sudo npm install -g less
   ```
3. **Sass compiler**  
   ```bash
   sudo gem install sass
   ```
4. **Docker (optional, for Elasticsearch)**  
   ```bash
   sudo apt install -y docker.io
   sudo usermod -aG docker $USER
   newgrp docker
   ```
   Run Elasticsearch:
   ```bash
   docker run -d --name elasticsearch      -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300      -e "discovery.type=single-node"      docker.elastic.co/elasticsearch/elasticsearch:7.17.6
   ```

### Configuration

1. Clone the repo:  
   ```bash
   git clone https://github.com/MicroPyramid/opensource-job-portal.git
   cd opensource-job-portal
   ```
2. Create and activate a virtual environment:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Copy the example env file and generate a secret key:  
   ```bash
   cp env.md .env
   sed -i 's/^SECRET_KEY=.*/SECRET_KEY="$(openssl rand -base64 50)"/' .env
   ```
4. Install Python dependencies:  
   ```bash
   pip install --upgrade pip
   pip install pipdeptree black pip-check
   pip install -r requirements.txt
   ```

### Database Setup & Data Seeding

1. Switch to the `postgres` user and set a password if needed:  
   ```bash
   sudo -u postgres psql
   ALTER USER postgres PASSWORD 'your_secure_password';
   \q
   ```
2. Create the database and import schema/data:  
   ```bash
   sudo -u postgres createdb peeljobs
   sudo -u postgres psql peeljobs < init_db/db_init.sql
   ```
3. Load initial fixtures:  
   ```bash
   python manage.py migrate
   for fixture in industries qualification skills countries states cities; do
     python manage.py loaddata $fixture
   done
   ```

### Running the App

1. Build front-end assets:  
   ```bash
   npm run build
   ```
2. Update the Elasticsearch index:  
   ```bash
   python manage.py update_index
   ```
3. Create an admin user:  
   ```bash
   python manage.py createsuperuser
   ```
4. Start the development server:  
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

Visit <http://localhost:8000> to see the portal in action!

---

## Usage

- **Post a Job**: Log in as a recruiter → Dashboard → “Post New Job”  
- **Search Jobs**: Enter keywords or filters on the homepage  
- **Receive Alerts**: Opt in for email notifications on your profile  
- **Manage Listings**: Copy, deactivate, or edit existing job posts  

For detailed API docs and integration guides, see the Read the Docs site:  
https://opensource-job-portal.readthedocs.io/en/latest/

---

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/awesome-feature`)  
3. Commit your changes (`git commit -m "Add awesome feature"`)  
4. Push to your fork (`git push origin feature/awesome-feature`)  
5. Open a Pull Request  

Please run `black .` and `pipdeptree` before submitting. All new features should include tests.

---

## License

This project is licensed under the **MIT License**. See LICENSE for details.

---

Happy coding! 🚀
