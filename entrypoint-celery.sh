#!/usr/bin/env bash

if [[ -z $PEEWEE_DATABASE_URL ]] ; then
  if [[ $PEEWEE_USER && $PEEWEE_PASS ]]; then
    PEEWEE_USER_PART="${PEEWEE_USER}:${PEEWEE_PASS}@"
  fi
  if [[ $PEEWEE_PORT ]] ; then
    PEEWEE_ADDR_PART="${PEEWEE_ADDR}:${PEEWEE_PORT}"
  else
    PEEWEE_ADDR_PART=$PEEWEE_ADDR
  fi
  PEEWEE_DATABASE_URL="${PEEWEE_PROTO}://${PEEWEE_USER_PART}${PEEWEE_ADDR_PART}/${PEEWEE_DATABASE}"
fi
if ! [[ -d "~/.pacifica-proxymod/" ]] ; then
  mkdir ~/.pacifica-proxymod/
fi
if ! [[ -f "~/.pacifica-proxymod/config.ini" ]] ; then
  printf "[database]\npeewee_url = \"${PEEWEE_DATABASE_URL}\"" > ~/.pacifica-proxymod/config.ini
fi
if ! [[ -f "~/.pacifica-proxymod/cpconfig.ini" ]] ; then
  printf "[global]\nlog.screen: True\nlog.access_file: 'access.log'\nlog.error_file: 'error.log'\nserver.socket_host: '0.0.0.0'\nserver.socket_port: 8069\nengine.autoreload.on: False\n\n[/]\nrequest.dispatch: cherrypy.dispatch.MethodDispatcher()" > ~/.pacifica-proxymod/cpconfig.ini
fi
celery -A "pacifica.proxymod.__main__" worker --loglevel="info"
