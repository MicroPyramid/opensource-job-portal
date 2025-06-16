Dear Copilot,

## Project Overview

PeelJobs is a dynamic, user-centric job board platform designed to streamline the entire hiring process, from job posting to application management. Built with modern web technologies, it offers a seamless experience for job seekers, recruiters, and administrators through robust role-based access control (RBAC).
Each user role is equipped with tailored functionalities to enhance efficiency, engagement, and management, ensuring a streamlined and secure recruitment process.

user types we have
    
-   company
    -   recruiter(s)
    -   Admin
-   job seeker
-   super admin - to manage whole platform
    -   support user - with restricted access to certain functionality and reports based on roles.

## Project Context

PeelJobs is a modern job board application built with:
- **Framework**: django 5.2
- **Styling**: bootstrap and migrating to tailwind 4.1.x css one by one with a new base template
- **Database**: postgresql
- **Icons**: fontawesome, we are migrating to lucide icons

## Project Goals
Migrate from old packages to new packages, ensuring that the application remains functional and up-to-date with the latest standards.


## Code Guidelines
- Use clear, descriptive variable and function names.
- Follow PEP 8 style guidelines for Python code.
- Use consistent naming conventions for files and directories.
- don't use gradients in tailwind css, use solid colors instead.