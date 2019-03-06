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
import typing
import uuid

import peewee

def create_peewee_model(db: peewee.Database) -> object:
    class EventModel(peewee.Model):
        uuid = peewee.UUIDField(default=uuid.uuid4, index=True, primary_key=True)

        event_type = peewee.CharField(index=True, null=True)
        event_type_version = peewee.CharField(index=True, null=True)
        cloud_events_version = peewee.CharField(index=True, null=True)
        source = peewee.CharField(index=True, null=True)
        event_id = peewee.CharField(index=True, null=True)
        event_time = peewee.CharField(index=True, null=True)
        schema_url = peewee.CharField(index=True, null=True)
        content_type = peewee.CharField(index=True, null=True)

        data = peewee.TextField()

        task_id = peewee.UUIDField(index=True, unique=True)
        task_status = peewee.CharField(index=True)

        exc_type = peewee.CharField(null=True)
        exc_value = peewee.CharField(null=True)
        exc_traceback = peewee.TextField()

        created = peewee.DateTimeField(default=datetime.datetime.now, index=True)
        updated = peewee.DateTimeField(default=datetime.datetime.now, index=True)
        deleted = peewee.DateTimeField(index=True, null=True)

        class Meta(object):
            database = db

    return EventModel

__all__ = ('create_peewee_model')
