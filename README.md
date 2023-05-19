# DBRegatta
Management software for a Dragon Boat regatta written in Python with Django

## Prerequisites
* Python 3.10
* Django including additional packages

To install all the additional dependencies used by Django, run:
```
pip install -r requirements.txt
```

## Getting started
After checkout, set up the database using the following command:
```
python manage.py migrate
```

If the database layout is changed thorugh a code change, run
```
python manage.py makemigrations
```
to update the database and migrate those changes with
```
python manage.py migrate
```
again.

## Startup
Run the DBRegatta Django web app, type:
```
python manage.py runserver [<ip>:]<port>
```
This should launch the Django webserver serving the app on the IP address and port specified. To bind on all interfaces, use `0.0.0.0` as the IP address. If the IP address is being omitted, the server will launch on localhost (`127.0.0.1`).

## Manage the site
To configure anything on the site, you need to create a superuser first. To do this, simply type:
```
python manage.py createsuperuser
```
and follow the instructions.
After a superuser is created, you can log in to the site using the credentials just created. Superusers can access the Django admin interface and create additional users there as well as configure all the endless config options exposed through Constance in the admin interface.
