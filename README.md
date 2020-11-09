## [Open source job portal](https://peeljobs.com)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/105a3bf03bec4cfbac70d7c30e574bea)](https://www.codacy.com/manual/ashwin/opensource-job-portal?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=MicroPyramid/opensource-job-portal&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/MicroPyramid/opensource-job-portal.svg?branch=master)](https://travis-ci.org/MicroPyramid/opensource-job-portal)
[![Coverage Status](https://coveralls.io/repos/github/MicroPyramid/opensource-job-portal/badge.svg?branch=master)](https://coveralls.io/github/MicroPyramid/opensource-job-portal?branch=master)

- Please visit [OpenSourceJobPortal](https://opensource-job-portal.readthedocs.io/en/latest/) for the latest documentation with unlimited free job posting, Social Api's authentication.

- Opensource Job Portal developed using python, django framework with unlimited free job posting and Social Api's authentication.

## Recruiter

Recruiter can register using email or google login to post job.
- Can post jobs to social networking sites like facebook, twitter, linkedin.
- Walk-in's
- Copy An Existing Job Post, Deactivate.
- Add localtion in Google Maps
- Post their job to social networking sites.

## Portal
- Job Alerts
- New Mobile Design
- Normal Search and Advanced Search
- Email Notifications


## Setup
Following are the setup instruction for ubuntu 18.04.

```bash
sudo apt install git postgresql python3 python3-dev python3-venv libpq-dev build-essential ruby ruby-dev gem redis-server memcached redis-tools -y
curl -sL https://deb.nodesource.com/setup_12.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt-get install node-less
```

##### Install and configure sass and less compilers
```bash
sudo gem install sass
```

You need to create symbolic link if you get error locating lessc
here my lessc file locatin is /usr/bin/lessc
you can find yours with this command ```which lessc```

```bash
sudo ln -s /usr/bin/lessc /usr/local/bin/lessc
```


##### Then setup env using the following command
```bash
python3 -m venv peeljobs-env
```

##### Activate env with the following command
```bash
activate peeljobs-env/bin/activate
```

##### Install requirements

```bash
pip install -r requirements.txt
```

For env variables, refer to env.md in source directory and you need to create a .env file to keep all env variables with their respective values.

##### Adding domains to hosts

Run the following command to add desired domains like below.
```bash
sudo nano /etc/hosts
```
```127.0.0.1```   ```test.peeljobs.com```


Then open `http://test.peeljobs.com:8000` in your borwser and it should work properly.

or

You too can run `http://localhost:8000`

##### Run docker
```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:2.4
```

##### Create index

Finally ```update_index``` command will freshen all of the content in your index. It iterates through all indexed models and updates the records in the index.
```bash
python manage.py update_index
```
