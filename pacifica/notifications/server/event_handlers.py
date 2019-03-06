#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/server/event_handlers.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import abc

from cloudevents.model import Event

class EventHandler(abc.ABC):
    def __init__(self) -> None:
        super(EventHandler, self).__init__()

    @abc.abstractmethod
    def handle(self, event: Event) -> None: # pragma: no cover
        raise NotImplementedError()

class NoopEventHandler(EventHandler):
    def __init__(self) -> None:
        super(NoopEventHandler, self).__init__()

    def handle(self, event: Event) -> None:
        pass

__all__ = ('EventHandler', 'NoopEventHandler')
