#!/bin/bash

service_name="nolsatu_courses"

cd /var/www/html/nolsatu-courses/
source env/bin/activate
git pull origin master &&
pip install -r requirements.txt
./manage.py collecstatic --noinput
./manage.py migrate
./manage.py test tests
systemctl restart $service_name