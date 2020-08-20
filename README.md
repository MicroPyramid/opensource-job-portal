opensource job portal
=====================

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/105a3bf03bec4cfbac70d7c30e574bea)](https://www.codacy.com/manual/ashwin/opensource-job-portal?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=MicroPyramid/opensource-job-portal&amp;utm_campaign=Badge_Grade)

[![Build Status](https://travis-ci.org/MicroPyramid/opensource-job-portal.svg?branch=master)](https://travis-ci.org/MicroPyramid/opensource-job-portal)

[![Coverage Status](https://coveralls.io/repos/github/MicroPyramid/opensource-job-portal/badge.svg?branch=master)](https://coveralls.io/github/MicroPyramid/opensource-job-portal?branch=master)

https://opensource-job-portal.readthedocs.io/en/latest/ for latest documentation
Job Portal with Unlimited free job posting, Social Api's authentication.

Opensource Job Portal developed in python django with Unlimited free job posting, Social Api's authentication.

# Recruiter
* Can post jobs to social networking sites like facebook, twitter, linkedin.
* Walk-in's
* Copy An Existing Job Post, Deactivate.
* Add localtion in Google Maps
* Post their job to social networking sites.

# Portal
* Job Alerts
* New Mobile Design
* Normal Search and Advanced Search
* Email Notifications


# Setup
These are setup instruction for ubuntu 18.04

```
sudo apt install git postgresql python3 python3-dev python3-venv libpq-dev build-essential ruby ruby-dev gem redis-server memcached redis-tools -y
curl -sL https://deb.nodesource.com/setup_12.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt-get install node-less
```

Install and configure sass and less compilers
```
sudo gem install sass
```

you need to create symbolic link if you get error locating lessc
here my lessc file locatin is /usr/bin/lessc
you can find yours with this command ```which lessc```
```
sudo ln -s /usr/bin/lessc /usr/local/bin/lessc
```


Then setup env using the following command
```
python3 -m venv peeljobs-env
```

Activate env with the following command
```
activate peeljobs-env/bin/activate
```

Install requirements
```
pip install -r requirements.txt
```

For env variables, refer to env.md for environment variables and keep those in the .env file in the current folder as your project is in.

Then open http://localhost:8000 in your borwser and it should work properly.

Run docker
```
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:2.4
```

create index
```
python manage.py update_index
```
