#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/models.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import abc
import json
import os
import typing

from cloudevents.model import Event
from jsonpath2.path import Path

from pacifica.notifications.client.exceptions import InvalidEventTypeValueError, InvalidSourceValueError, TransactionDuplicateAttributeError
from pacifica.notifications.client.globals import CLOUDEVENTS_DEFAULT_EVENT_TYPE_, CLOUDEVENTS_DEFAULT_SOURCE_

class PacificaModel(abc.ABC):
    def __init__(self) -> None:
        super(PacificaModel, self).__init__()

    @classmethod
    @abc.abstractmethod
    def from_cloudevents_model(cls, event: Event) -> typing.Union['PacificaModel', typing.List['PacificaModel']]: # pragma: no cover
        raise NotImplementedError()

class File(PacificaModel):
    def __init__(self, **attrs: typing.Dict[str, typing.Any]) -> None:
        super(File, self).__init__()

        for name in ['_id', 'ctime', 'encoding', 'hashsum', 'hashtype', 'mimetype', 'mtime', 'name', 'size', 'subdir', 'suspense_date']:
            setattr(self, name, None)

            if name in attrs:
                setattr(self, name, attrs.get(name, None))


    @classmethod
    def from_cloudevents_model(cls, event: Event) -> typing.List['File']:
        if CLOUDEVENTS_DEFAULT_EVENT_TYPE_ != event.event_type:
            raise InvalidEventTypeValueError(event)

        if CLOUDEVENTS_DEFAULT_SOURCE_ != event.source:
            raise InvalidSourceValueError(event)

        insts = []

        for match_data in Path.parse_str('$[*][?(@["destinationTable"] = "Files")]').match(event.data):
            inst = cls(**match_data.current_value)

            insts.append(inst)

        return insts

    @property
    def path(self) -> str:
        if self.name is None:
            raise AttributeError('field \'name\' is None')
        elif self.subdir is None:
            return self.name
        else:
            return os.path.join(self.subdir, self.name)

class Transaction(PacificaModel):
    def __init__(self, **attrs: typing.Dict[str, typing.Any]) -> None:
        super(Transaction, self).__init__()

        for name in ['_id', 'analytical_tool', 'description', 'instrument', 'proposal', 'submitter', 'suspense_date']:
            setattr(self, name, None)

            if name in attrs:
                setattr(self, name, attrs.get(name, None))

    @classmethod
    def from_cloudevents_model(cls, event: Event) -> 'Transaction':
        if CLOUDEVENTS_DEFAULT_EVENT_TYPE_ != event.event_type:
            raise InvalidEventTypeValueError(event)

        if CLOUDEVENTS_DEFAULT_SOURCE_ != event.source:
            raise InvalidSourceValueError(event)

        attrs = {}

        for name in ['_id', 'analytical_tool', 'description', 'instrument', 'proposal', 'submitter', 'suspense_date']:
            for match_data in Path.parse_str('$[*][?(@["destinationTable"] = {0})]["value"]'.format(json.dumps('Transactions.{0}'.format(name)))).match(event.data):
                if name in attrs:
                    raise TransactionDuplicateAttributeError(event, name)

                attrs[name] = match_data.current_value

            if name not in attrs:
                attrs[name] = None

        return cls(**attrs)

class TransactionKeyValue(PacificaModel):
    def __init__(self, **attrs: typing.Dict[str, typing.Any]) -> None:
        super(TransactionKeyValue, self).__init__()

        for name in ['key', 'value']:
            setattr(self, name, None)

            if name in attrs:
                setattr(self, name, attrs.get(name, None))

    @classmethod
    def from_cloudevents_model(cls, event: Event) -> typing.List['TransactionKeyValue']:
        if CLOUDEVENTS_DEFAULT_EVENT_TYPE_ != event.event_type:
            raise InvalidEventTypeValueError(event)

        if CLOUDEVENTS_DEFAULT_SOURCE_ != event.source:
            raise InvalidSourceValueError(event)

        insts = []

        for match_data in Path.parse_str('$[*][?(@["destinationTable"] = "TransactionKeyValue")]').match(event.data):
            inst = cls(**match_data.current_value)

            insts.append(inst)

        return insts

__all__ = ('PacificaModel', 'File', 'Transaction', 'TransactionKeyValue')
