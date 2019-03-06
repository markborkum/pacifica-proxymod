#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/proxymod/__main__.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import argparse
import os
import threading
import time

import cherrypy
import playhouse.db_url

from pacifica.notifications.server.config import get_config, get_config_file_path
from pacifica.notifications.server.orm import create_peewee_model
from pacifica.notifications.server.rest import create_cherrypy_app
from pacifica.notifications.server.tasks import create_celery_app
from pacifica.proxymod.router import router

CONFIG_FILE_PATH_ = get_config_file_path(key='PACIFICA_PROXYMOD_CONFIG', dirname='.pacifica-proxymod', basename='config.ini')

CHERRYPY_CONFIG_FILE_PATH_ = get_config_file_path(key='PACIFICA_PROXYMOD_CPCONFIG', dirname='.pacifica-proxymod', basename='cpconfig.ini')

EventModel = create_peewee_model(playhouse.db_url.connect(get_config(CONFIG_FILE_PATH_).get('database', 'peewee_url')))

EventModel.create_table(safe=True)

celery_app = create_celery_app(EventModel, router, name='pacifica.proxymod.tasks', receive_task_name='pacifica.proxymod.tasks.receive', backend=os.getenv('BACKEND_URL', 'rpc://'), broker=os.getenv('BROKER_URL', 'pyamqp://'))

Root = create_cherrypy_app(EventModel, celery_app.tasks['pacifica.proxymod.tasks.receive'])

application = cherrypy.Application(Root(), '/', config=CHERRYPY_CONFIG_FILE_PATH_)

if __name__ == '__main__':
    def _stop_later(secs) -> None:
        def _sleep_then_exit() -> None:
            time.sleep(secs)

            cherrypy.engine.exit()

            return

        sleep_thread = threading.Thread(target=_sleep_then_exit)
        sleep_thread.daemon = True
        sleep_thread.start()

        return

    parser = argparse.ArgumentParser(description='Run the notifications server.')
    parser.add_argument('-c', '--config', metavar='CONFIG', type=str, default=CHERRYPY_CONFIG_FILE_PATH_, dest='config', help='cherrypy config file')
    parser.add_argument('-p', '--port', metavar='PORT', type=int, default=8069, dest='port', help='port to listen on')
    parser.add_argument('-a', '--address', metavar='ADDRESS', type=str, default='localhost', dest='address', help='address to listen on')
    parser.add_argument('--stop-after-a-moment', help=argparse.SUPPRESS, default=False, dest='stop_later', action='store_true')

    args = parser.parse_args()

    if args.stop_later:
        _stop_later(20)

    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port,
    })
    cherrypy.quickstart(Root(), '/', config=args.config)

__all__ = ('EventModel', 'Root', 'application', 'celery_app')
