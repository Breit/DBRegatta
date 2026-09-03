# DBRegatta
Management software for a Dragon Boat regatta written in Python with Django

## Prerequisites
* Python 3.12+
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

`runserver` is a development-only server and should not be used in production - see [Production deployment](#production-deployment) below.

## Manage the site
To configure anything on the site, you need to create a superuser first. To do this, simply type:
```
python manage.py createsuperuser
```
and follow the instructions.
After a superuser is created, you can log in to the site using the credentials just created. Superusers can access the Django admin interface and create additional users there as well as configure all the endless config options exposed through Constance in the admin interface.

## Production deployment
In production, the app is served by [Gunicorn](https://gunicorn.org/) (a WSGI server) supervised by the OS's init system - `systemd` on Linux, or `rc.d` on FreeBSD - and put behind a reverse proxy (e.g. Apache) that terminates HTTPS.

The `deploy/` folder contains the scripts for this:
* `deploy/config` - per-instance settings (user/group, port, service name, git branch, etc.). Copy the whole `deploy/` folder once per instance you want to run side-by-side, and give each copy a unique `SERVICE_NAME`/`PORT` in its own `config`.
* `deploy/helpers` - shared shell functions (portable `sed -i`, and starting/stopping/installing the service on either systemd or rc.d). Sourced by both `deploy/deploy` and `deploy/run`.
* `deploy/deploy` - (re)installs the app: stops the service, clones/hard-resets the checkout to the configured branch, creates the venv if needed, installs dependencies, runs migrations, sets `DEBUG = False`, a fresh `SECRET_KEY`, and `CSRF_TRUSTED_ORIGINS`, runs `collectstatic`, then (re)generates and (re)starts the systemd unit/rc.d script from the templates checked into the repo (`deploy/dbregatta.service`/`deploy/dbregatta.rc`).
* `deploy/run` - convenience shortcut to just restart the already-installed service (e.g. from a cron job).

To set up a new instance on the server:
1. Create a directory for the instance, e.g. `/srv/dbregatta-<instance>`.
2. Copy `deploy/config`, `deploy/deploy`, `deploy/run` and `deploy/helpers` into it.
3. Edit `config` for that instance - at minimum give it a unique `SERVICE_NAME` and `PORT` if you're running more than one instance on the same server.
4. `chmod +x deploy run`
5. Run `./deploy` (as root) - this checks out the code, creates the venv, installs dependencies, migrates the DB, and installs/starts the service. Re-run it any time to update the instance to the latest commit on `BRANCH`.

Apache (or any reverse proxy in front of it) needs to:
* Proxy requests to `127.0.0.1:<PORT>` (the port configured in `deploy/config`).
* Set the `X-Forwarded-Proto` header to `https` so Django's `SECURE_SSL_REDIRECT` doesn't cause a redirect loop.
* Serve `/static/` directly from `STATIC_ROOT` (`content/static/`) rather than proxying it to the app.
