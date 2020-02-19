# Note this base image is based on debian
FROM python:3.6.8
MAINTAINER Alison Mukoma<mukomalison@gmail.com>

RUN export DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND noninteractive
RUN dpkg-divert --local --rename --add /sbin/initctl

RUN apt-get install -y --fix-missing && apt-get update -y && apt-get autoremove -y

RUN apt-get install -y python3-pip \
	python-gdal \
	python3-dev \
	python-geoip \
	rpl \
	faketime \
	tzdata \
	strace \
	lsof \
	zlib1g-dev \
	libfreetype6-dev \
	liblcms2-dev \
	libwebp-dev \
	tcl8.6-dev \
	tk8.6-dev \
	python-tk \
	libxml2-dev \
	libxslt1-dev \
	build-essential \
	libssl-dev \
	libffi-dev \
	apt-utils \
	curl \
	wget \
	libpq-dev \
	gem \
	ruby \
	ruby-dev \
	build-essential \
	libssl-dev \
	libffi-dev \
	sass \
	less \
	libtiff5-dev \
	libharfbuzz-dev \
	libfribidi-dev \
	rubygems \
	rubygems-integration \
	node-less

RUN gem install sass  

# Install Node js
RUN curl -sL https://deb.nodesource.com/setup_13.x | bash -
RUN apt-get -y install nodejs npm

# Debian is messed up and aliases node as nodejs
# So when yuglify is installed it references the wrong node binary...
# lets fix that here...

#RUN rpl "env node" "env nodejs" /usr/lib/node_modules/yuglify/bin/yuglify

# Install grunt
# RUN npm install -g grunt-cli


RUN apt-get -y install yui-compressor

ENV ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install --upgrade setuptools
RUN pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi
RUN pip install uwsgitop
RUN pip install pyrasite


#USER www-data
WORKDIR /home/web/django_project

ADD uwsgi.conf /uwsgi.conf

# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

CMD ["uwsgi", "--ini", "/uwsgi.conf"]
