#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/server/rest.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import json
import typing
import uuid

import celery
import cherrypy
import peewee

def create_cherrypy_app(cls, receive_task: celery.Task) -> object:
    def error_page_default(**kwargs: typing.Dict[str, typing.Any]) -> bytes:
        cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return bytes(json.dumps(kwargs), 'utf-8')

    class Receive(object):
        _cp_config = {
            'error_page.default': error_page_default,
        }

        exposed = True

        def POST(self) -> bytes:
            event_data = json.loads(cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length'])))

            async_result = receive_task.delay(event_data)

            cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            cherrypy.response.status = '200 OK'
            return bytes(json.dumps(str(async_result.id)), 'utf-8')

    class Status(object):
        _cp_config = {
            'error_page.default': error_page_default,
        }

        exposed = True

        def GET(self, task_id: str) -> bytes:
            try:
                inst = cls.get(task_id=uuid.UUID(task_id))
            except peewee.DoesNotExist:
                raise cherrypy.HTTPError('404', 'Not Found')

            cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            cherrypy.response.status = '200 OK'
            return bytes(json.dumps(inst.task_status), 'utf-8')

    class Root(object):
        _cp_config = {
            'error_page.default': error_page_default,
        }

        exposed = True

        receive = Receive()
        status = Status()

        def GET(self) -> bytes:
            cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            cherrypy.response.status = '200 OK'
            return bytes(json.dumps(list(map(lambda inst: {
                'eventType': inst.event_type,
                'eventTypeVersion': inst.event_type_version,
                'source': inst.source,
                'eventID': inst.event_id,
                'eventTime': inst.event_time,
                'schemaURL': inst.schema_url,
                'contentType': inst.content_type,
                # 'data': inst.data,
                'taskID': str(inst.task_id),
                'taskStatus': inst.task_status,
                # 'exceptionType': inst.exc_type,
                # 'exceptionValue': inst.exc_value,
                # 'exceptionTraceback': inst.exc_traceback,
                'created': str(inst.created),
                'updated': str(inst.updated),
                # 'deleted': str(inst.deleted),
            }, cls.select(*[
                cls.event_type,
                cls.event_type_version,
                cls.source,
                cls.event_id,
                cls.event_time,
                cls.schema_url,
                cls.content_type,
                # cls.data,
                cls.task_id,
                cls.task_status,
                # cls.exc_type,
                # cls.exc_value,
                # cls.exc_traceback,
                cls.created,
                cls.updated,
                # cls.deleted,
            ]).order_by(*[
                cls.created.desc(),
            ])))), 'utf-8')

    return Root

__all__ = ('create_cherrypy_app')
