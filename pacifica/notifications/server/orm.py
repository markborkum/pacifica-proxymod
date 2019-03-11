#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/server/orm.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import datetime
import json
import sys
import traceback
import typing
import uuid

import celery
import cherrypy
import peewee

from pacifica.notifications.client.router import RouteNotFoundRouterError, Router

def create_peewee_model(db: peewee.Database) -> object:
    class ReceiveTaskModel(peewee.Model):
        uuid = peewee.UUIDField(default=uuid.uuid4, index=True, primary_key=True)

        event_type = peewee.CharField(index=True, null=True)
        event_type_version = peewee.CharField(index=True, null=True)
        cloud_events_version = peewee.CharField(index=True, null=True)
        source = peewee.CharField(index=True, null=True)
        event_id = peewee.CharField(index=True, null=True)
        event_time = peewee.CharField(index=True, null=True)
        schema_url = peewee.CharField(index=True, null=True)
        content_type = peewee.CharField(index=True, null=True)

        event_data = peewee.TextField()
        data = peewee.TextField()

        task_id = peewee.UUIDField(index=True, unique=True)
        task_application_name = peewee.CharField(index=True)
        task_name = peewee.CharField(index=True)
        task_status = peewee.CharField(index=True)

        exc_type = peewee.CharField(null=True)
        exc_value = peewee.CharField(null=True)
        exc_traceback = peewee.TextField()

        created = peewee.DateTimeField(default=datetime.datetime.now, index=True)
        updated = peewee.DateTimeField(default=datetime.datetime.now, index=True)
        deleted = peewee.DateTimeField(index=True, null=True)

        class Meta(object):
            database = db

        @classmethod
        def create_celery_app(cls, router: Router, name: str, receive_task_name: str, *args, **kwargs) -> celery.Celery:
            celery_app = celery.Celery(name, *args, **kwargs)

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

                    'event_data': json.dumps(event_data),
                    'data': json.dumps(event_data.get('data', None)),

                    'task_id': self.request.id,
                    'task_application_name': name,
                    'task_name': receive_task_name,
                    'task_status': '202 Accepted',

                    'exc_type': None,
                    'exc_value': None,
                    'exc_traceback': '',
                })
                inst.save(force_insert=True)

                try:
                    route = router.match_first_or_raise(event_data)
                except RouteNotFoundRouterError:
                    inst.task_status = '422 Unprocessable Entity'
                    inst.save()
                else:
                    inst.task_status = '102 Processing'
                    inst.save()

                    try:
                        route(event_data)
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

        @classmethod
        def create_cherrypy_app(cls, receive_task: celery.Task) -> cherrypy.Application:
            class Get(object):
                exposed = True

                def GET(self, task_id: str) -> bytes:
                    try:
                        inst = cls.get(task_id=uuid.UUID(task_id))
                    except peewee.DoesNotExist:
                        raise cherrypy.HTTPError('404', 'Not Found')
                    except ValueError:
                        raise cherrypy.HTTPError('422', 'Unprocessable Entity')

                    cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                    cherrypy.response.status = '200 OK'
                    return bytes(json.dumps({
                        'eventType': inst.event_type,
                        'eventTypeVersion': inst.event_type_version,
                        'source': inst.source,
                        'eventID': inst.event_id,
                        'eventTime': inst.event_time,
                        'schemaURL': inst.schema_url,
                        'contentType': inst.content_type,
                        'eventData': inst.event_data,
                        'data': inst.data,
                        'taskID': str(inst.task_id),
                        'taskStatus': inst.task_status,
                        'taskApplicationName': inst.task_application_name,
                        'taskName': inst.task_name,
                        'exceptionType': inst.exc_type,
                        'exceptionValue': inst.exc_value,
                        'exceptionTraceback': inst.exc_traceback,
                        'created': str(inst.created) if inst.created is not None else None,
                        'updated': str(inst.updated) if inst.updated is not None else None,
                        'deleted': str(inst.deleted) if inst.deleted is not None else None,
                    }), 'utf-8')

            class Receive(object):
                exposed = True

                def POST(self) -> bytes:
                    event_data = json.loads(cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length'])))

                    async_result = receive_task.delay(event_data)

                    cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                    cherrypy.response.status = '200 OK'
                    return bytes(json.dumps(str(async_result.id)), 'utf-8')

            class Status(object):
                exposed = True

                def GET(self, task_id: str) -> bytes:
                    try:
                        inst = cls.get(task_id=uuid.UUID(task_id))
                    except peewee.DoesNotExist:
                        raise cherrypy.HTTPError('404', 'Not Found')
                    except ValueError:
                        raise cherrypy.HTTPError('422', 'Unprocessable Entity')

                    cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                    cherrypy.response.status = '200 OK'
                    return bytes(json.dumps(inst.task_status), 'utf-8')

            class Root(object):
                exposed = True

                get = Get()
                receive = Receive()
                status = Status()

                def GET(self) -> bytes:
                    cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                    cherrypy.response.status = '200 OK'
                    return bytes(json.dumps(list(map(lambda inst: {
                        # 'eventType': inst.event_type,
                        # 'eventTypeVersion': inst.event_type_version,
                        # 'source': inst.source,
                        # 'eventID': inst.event_id,
                        # 'eventTime': inst.event_time,
                        # 'schemaURL': inst.schema_url,
                        # 'contentType': inst.content_type,
                        # 'eventData': inst.event_data,
                        # 'data': inst.data,
                        'taskID': str(inst.task_id),
                        # 'taskStatus': inst.task_status,
                        # 'taskApplicationName': inst.task_application_name,
                        # 'taskName': inst.task_name,
                        # 'exceptionType': inst.exc_type,
                        # 'exceptionValue': inst.exc_value,
                        # 'exceptionTraceback': inst.exc_traceback,
                        'created': str(inst.created) if inst.created is not None else None,
                        'updated': str(inst.updated) if inst.updated is not None else None,
                        'deleted': str(inst.deleted) if inst.deleted is not None else None,
                    }, cls.select(*[
                        # cls.event_type,
                        # cls.event_type_version,
                        # cls.source,
                        # cls.event_id,
                        # cls.event_time,
                        # cls.schema_url,
                        # cls.content_type,
                        # cls.event_data,
                        # cls.data,
                        cls.task_id,
                        # cls.task_application_name,
                        # cls.task_name,
                        # cls.task_status,
                        # cls.exc_type,
                        # cls.exc_value,
                        # cls.exc_traceback,
                        cls.created,
                        cls.updated,
                        cls.deleted,
                    ]).order_by(*[
                        cls.created.desc(),
                    ])))), 'utf-8')

            def error_page_default(**kwargs: typing.Dict[str, typing.Any]) -> bytes:
                cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                return bytes(json.dumps(kwargs), 'utf-8')

            application = cherrypy.Application(Root(), '/', config={
                '/': {
                    'error_page.default': error_page_default,
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                },
            })

            return application

    return ReceiveTaskModel

__all__ = ('create_peewee_model')
