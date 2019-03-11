#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/exceptions.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

from cloudevents.model import Event

from .globals import CLOUDEVENTS_DEFAULT_EVENT_TYPE_, CLOUDEVENTS_DEFAULT_SOURCE_

class EventError(BaseException):
    def __init__(self, event: Event) -> None:
        super(EventError, self).__init__()

        self.event = event

class InvalidEventTypeValueError(EventError):
    def __str__(self) -> str: # pragma: no cover
        return 'field \'event_type\' is invalid (expected: \'{0}\')'.format(CLOUDEVENTS_DEFAULT_EVENT_TYPE_.replace('\'', '\\\''))

class InvalidSourceValueError(EventError):
    def __str__(self) -> str: # pragma: no cover
        return 'field \'source\' is invalid (expected: \'{0}\')'.format(CLOUDEVENTS_DEFAULT_SOURCE_.replace('\'', '\\\''))

class TransactionDuplicateAttributeError(EventError):
    def __init__(self, event: Event, name: str) -> None:
        super(TransactionDuplicateAttributeError, self).__init__(event)

        self.name = name

    def __str__(self) -> str: # pragma: no cover
        return 'field \'Transactions.{0}\' is already defined'.format(self.name.replace('\'', '\\\''))

__all__ = ('EventError', 'InvalidEventTypeValueError', 'InvalidSourceValueError', 'TransactionDuplicateAttributeError')
