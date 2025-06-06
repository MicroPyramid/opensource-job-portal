# PeelJobs - Dynamic Job Board Platform

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/105a3bf03bec4cfbac70d7c30e574bea)](https://www.codacy.com/manual/ashwin/opensource-job-portal?utm_source=github.com&utm_medium=referral&utm_content=MicroPyramid/opensource-job-portal&utm_campaign=Badge_Grade)  
[![Build Status](https://travis-ci.org/MicroPyramid/opensource-job-portal.svg?branch=master)](https://travis-ci.org/MicroPyramid/opensource-job-portal)  
[![Coverage Status](https://coveralls.io/repos/github/MicroPyramid/opensource-job-portal/badge.svg?branch=master)](https://coveralls.io/github/MicroPyramid/opensource-job-portal?branch=master)

**PeelJobs** is a dynamic, user-centric job board platform designed to streamline the entire hiring process, from job posting to application management. Built with modern web technologies, it offers a seamless experience for job seekers, recruiters, and administrators through robust role-based access control (RBAC).

🔗 **Documentation**: https://opensource-job-portal.readthedocs.io/en/latest/  
📋 **Setup Guide**: See [SETUP.md](SETUP.md) for complete development and deployment instructions

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Core Features](#core-features)
4. [Technology Stack](#technology-stack)
5. [Quick Start](#quick-start)
6. [Usage Guide](#usage-guide)
7. [Contributing](#contributing)
8. [License](#license)

---

## Project Overview

PeelJobs transforms the traditional hiring process by providing a comprehensive platform that serves multiple user types with tailored functionalities. Each role is equipped with specific tools to enhance efficiency, engagement, and management, ensuring a streamlined and secure recruitment process.

### Mission
To democratize job searching and hiring by providing a powerful, free, and open-source platform that connects talent with opportunities efficiently.

### Vision
Creating the most user-friendly and feature-rich job board platform that scales from startups to enterprise-level recruitment needs.

---

## User Roles & Permissions

PeelJobs implements a comprehensive role-based access control system with distinct user types:

### 🏢 Company Users
- **Recruiters**: Post jobs, manage applications, conduct interviews
- **Company Admin**: Oversee company-wide recruitment activities and manage recruiter accounts

### 👤 Job Seekers
- **Candidates**: Search jobs, apply for positions, manage applications, receive alerts
- **Profile Management**: Build professional profiles with skills, experience, and preferences

### 🔧 Platform Administration
- **Super Admin**: Complete platform oversight and management capabilities
- **Support Staff**: Restricted access to specific functionality and reports based on assigned roles

---

## Core Features

### 🎯 For Recruiters & Companies
- **Smart Job Posting**: Create detailed job listings with rich formatting and media support
- **Application Management**: Streamlined applicant tracking and communication tools
- **Walk-in Events**: Schedule and manage on-site interview events with Google Maps integration
- **Bulk Operations**: Copy, edit, and manage multiple job postings efficiently
- **Analytics Dashboard**: Track job performance, application metrics, and hiring insights
- **Social Authentication**: Quick registration via Google OAuth and email/password

### 🔍 For Job Seekers
- **Intelligent Search**: Advanced filtering by location, salary, skills, and experience level
- **Real-time Alerts**: Personalized email notifications for matching opportunities
- **Application Tracking**: Comprehensive history of applied positions and their status
- **Profile Builder**: Professional profile creation with skill assessments and portfolio links
- **Mobile-Optimized**: Responsive design for seamless mobile job searching
- **Favorites System**: Save and organize interesting job opportunities

### ⚡ Technical Excellence
- **Lightning-Fast Search**: Elasticsearch-powered full-text search with instant results
- **Background Processing**: Redis + Celery for email notifications and heavy operations
- **Smart Caching**: Memcached integration for optimized page load times
- **RESTful APIs**: Comprehensive API endpoints for third-party integrations
- **Scalable Architecture**: Built to handle high traffic and large datasets
- **Security First**: Role-based permissions, secure authentication, and data protection

---

## Technology Stack

### Backend Infrastructure
- **Framework**: Django 4.2.22 (Python)
- **Database**: PostgreSQL with optimized queries
- **Search Engine**: Elasticsearch 7.17.6
- **Task Queue**: Celery 5.5.0 with Redis broker
- **Caching**: Redis + Memcached for multi-layer caching

### Frontend & UI
- **Styling**: Bootstrap 5 + Tailwind CSS 4.1.x (progressive migration)
- **Icons**: FontAwesome (migrating to Lucide Icons)
- **Build Tools**: Node.js, npm, Less/Sass compilation
- **Responsive Design**: Mobile-first approach with PWA capabilities

### Development & Operations
- **Code Quality**: Black formatter, Prospector linting, Coverage reporting
- **Testing**: Django Test Suite, BDD with Behave Django
- **CI/CD**: Travis CI integration with automated testing
- **Containerization**: Docker support for easy deployment
- **Monitoring**: Built-in admin tools and performance monitoring

---

## Quick Start

> **📋 For complete setup instructions, see [SETUP.md](SETUP.md)**

### Prerequisites
- Python 3.12+, PostgreSQL, Node.js, Redis

### Basic Setup
```bash
# Clone repository
git clone https://github.com/MicroPyramid/opensource-job-portal.git
cd opensource-job-portal

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
createdb peeljobs_dev
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**Access Points:**
- Application: http://localhost:8000
- Admin Panel: http://localhost:8000/admin/
- Schema Viewer: http://localhost:8000/schema-viewer/

---

## Usage Guide

### For Recruiters
1. **Register**: Create account via email/password or Google OAuth
2. **Post Jobs**: Dashboard → "Post New Job" → Fill details → Publish
3. **Manage Applications**: Review candidates, schedule interviews, track status
4. **Analytics**: Monitor job performance and application metrics

### For Job Seekers
1. **Search**: Use keyword filters on homepage for relevant opportunities
2. **Apply**: Click "Apply Now" and submit application with resume
3. **Track**: Monitor application status in your profile dashboard
4. **Alerts**: Enable email notifications for matching job opportunities

### For Administrators
1. **User Management**: Oversee user accounts and permissions
2. **Content Moderation**: Review and approve job postings
3. **Analytics**: Access platform-wide metrics and reports
4. **System Monitoring**: Track performance and usage statistics

---

## API Integration

PeelJobs provides comprehensive RESTful APIs for third-party integrations:

- **Job Listings API**: Retrieve and filter job postings
- **Application API**: Submit and track job applications
- **User Management API**: Handle user registration and profiles
- **Search API**: Advanced job search capabilities

For detailed API documentation, visit: [SETUP.md](SETUP.md)

---

## Contributing

We welcome contributions from the community! Here's how to get started:

### Development Process
1. **Fork** the repository on GitHub
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with proper tests
4. **Format** code with `black .` and check dependencies with `pipdeptree`
5. **Commit** changes (`git commit -m "Add amazing feature"`)
6. **Push** to your fork (`git push origin feature/amazing-feature`)
7. **Submit** a Pull Request with detailed description

### Code Standards
- Follow Django best practices and PEP 8
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages

### Areas for Contribution
- 🐛 Bug fixes and improvements
- 🔍 Enhanced search functionality
- 📱 Mobile experience optimization
- 🎨 UI/UX improvements
- 🔒 Security enhancements
- 📊 Analytics and reporting features

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Support & Community

- **Documentation**: https://opensource-job-portal.readthedocs.io/en/latest/
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

---

**Happy coding! 🚀**
