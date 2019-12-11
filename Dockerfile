from ubuntu
run apt-get update && apt-get upgrade -y && apt-get autoremove -y
run apt-get install -y apt-utils
run apt-get install -y curl wget libpq-dev python3-dev gem ruby ruby-dev build-essential libssl-dev libffi-dev python-dev python3-pip zsh
run gem install sass
run apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev tcl8.6-dev tk8.6-dev python-tk
run pip3 install --upgrade pip
run apt-get install -y npm
run npm install -g less
run ln -s /usr/bin/nodejs /usr/bin/node

# pip3 install -r /home/peeljobs/requirements.txt
