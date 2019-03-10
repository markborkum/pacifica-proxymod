# Pacifica Template Repository
[![Build Status](https://travis-ci.org/pacifica/pacifica-proxymod.svg?branch=master)](https://travis-ci.org/pacifica/pacifica-proxymod)
[![Build status](https://ci.appveyor.com/api/projects/status/eg2r1y37yvxi0b5p?svg=true)](https://ci.appveyor.com/project/dmlb2000/pacifica-proxymod)
[![Maintainability](https://api.codeclimate.com/v1/badges/f2dba248b1a7966e5a49/maintainability)](https://codeclimate.com/github/pacifica/pacifica-proxymod/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f2dba248b1a7966e5a49/test_coverage)](https://codeclimate.com/github/pacifica/pacifica-proxymod/test_coverage)

This is the Pacifica Notifications Service for [proxymod](https://github.com/IMMM-SFA/proxymod).

## The Parts

There are several parts to this code as it encompasses
integrating several python libraries together.

 * [PeeWee](http://docs.peewee-orm.com/en/latest/)
 * [CherryPy](https://cherrypy.org/)
 * [Celery](http://www.celeryproject.org/)

For each major library we have integration points in
specific modules to handle configuration of each library.

### PeeWee

The configuration of PeeWee is pulled from an INI file parsed
from an environment variable or command line option. The
configuration in the file is a database
[connection url](http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url).

 * [proxymod PeeWee Model](pacifica/proxymod/__main__.py#L29)
 * [proxymod Config Parser](pacifica/proxymod/__main__.py#L25)

### CherryPy

The CherryPy configuration has two entry points for use. The
WSGI interface and the embedded server through the main
method.

 * [proxymod Main Method](pacifica/proxymod/__main__.py#L37-L69)
 * [proxymod WSGI API](pacifica/proxymod/__main__.py#L35)
 * [proxymod CherryPy Objects](pacifica/proxymod/__main__.py#L33)

### Celery

The Celery tasks are located in their own module and have
an entry point from the CherryPy REST objects. The tasks
save state into a PeeWee database that is also accessed
in the CherryPy REST objects.

 * [proxymod Tasks](pacifica/proxymod/__main__.py#L31)

## Start Up Process

The default way to start up this service is with a shared
SQLite database. The database must be located in the
current working directory of both the celery workers and
the CherryPy web server. The messaging system in
[Travis](.travis.yml) and [Appveyor](appveyor.yml) is
Redis, however the default is RabbitMQ.

There are three commands needed to start up the services.
Perform these steps in three separate terminals.

 1. `docker-compose up rabbit`
 2. `env DATABASE_URL="sqliteext:///db.sqlite3" celery -A "pacifica.proxymod.__main__:celery_app" worker -l info`
 3. `env DATABASE_URL="sqliteext:///db.sqlite3" python3 -m "pacifica.proxymod.__main__"`

## Testing

To test, perform these steps:

 1. `python3 -m unittest pacifica/proxymod/tests/test_*.py`
