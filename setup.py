import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
PROJECT_NAME = "opensource_job_portal"

data_files = []
for dirpath, dirnames, filenames in os.walk(PROJECT_NAME):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len(PROJECT_NAME) + 1 :], f))

setup(
    name="opensource-job-portal",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    description="An opensourse Job Portal with Unlimited free job posting, Social Api authentication.",
    long_description=README,
    url="https://github.com/MicroPyramid/opensource-job-portal.git",
    author="Micropyramid",
    author_email="hello@micropyramid.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[],
)
