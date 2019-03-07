#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/server/tasks.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import json
import sys
import traceback
import typing

import celery

from pacifica.notifications.client.router import RouteNotFoundRouterError, Router

def create_celery_app(cls, router: Router, name: str = 'pacifica.notifications.server.tasks', receive_task_name: str = 'pacifica.notifications.server.tasks.receive', **kwargs) -> celery.Celery:
    celery_app = celery.Celery(name, **kwargs)

    celery_app.conf.worker_redirect_stdouts = False

    @celery_app.task(bind=True, ignore_result=True, name=receive_task_name)
    def receive_task(self, event_data: typing.Dict[str, typing.Any]) -> None:
        inst = cls(**{
            'event_type': event_data.get('eventType', None),
            'event_type_version': event_data.get('eventTypeVersion', None),
            'source': event_data.get('source', None),
            'event_id': event_data.get('eventID', None),
            'event_time': event_data.get('eventTime', None),
            'schema_url': event_data.get('schemaURL', None),
            'content_type': event_data.get('contentType', None),

            'data': json.dumps(event_data),

            'task_id': self.request.id,
            'task_status': '202 Accepted',

            'exc_type': None,
            'exc_value': None,
            'exc_traceback': '',
        })
        inst.save(force_insert=True)

        inst.task_status = '102 Processing'
        inst.save()

        try:
            router(event_data)
        except RouteNotFoundRouterError:
            inst.task_status = '422 Unprocessable Entity'
            inst.save()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            inst.exc_type = exc_type.__name__
            inst.exc_value = str(exc_value)
            inst.exc_traceback = traceback.format_tb(exc_traceback)

            inst.task_status = '500 Internal Server Error'
            inst.save()
        else:
            inst.task_status = '200 OK'
            inst.save()

        return

    return celery_app

__all__ = ('create_celery_app')
