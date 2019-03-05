#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/router.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import typing

from cloudevents.model import Event
from jsonpath2.path import Path

from pacifica.notifications.server.event_handlers import EventHandler

class Route(object):
    def __init__(self, path: Path, event_handler: EventHandler) -> None:
        super(Route, self).__init__()

        self.path = path

        self.event_handler = event_handler

    def __call__(self, event_data: typing.Dict[str, typing.Any]) -> None:
        event = Event(event_data)

        self.event_handler.handle(event)

        return

    def match(self, event_data: typing.Dict[str, typing.Any]) -> bool:
        for match_data in self.path.match(event_data):
            return True

        return False

class Router(object):
    def __init__(self) -> None:
        super(Router, self).__init__()

        self._routes = [] # type: typing.List[Route]

    def __call__(self, event_data: typing.Dict[str, typing.Any]) -> None:
        route = self.match_first_or_raise(event_data)

        route(event_data)

        return

    def add_route(self, *args, **kwargs) -> None:
        route = Route(*args, **kwargs)

        self._routes.append(route)

        return

    def match(self, event_data: typing.Dict[str, typing.Any]) -> typing.Generator[Route, None, None]:
        for route in self._routes:
            if route.match(event_data):
                yield route

    def match_first_or_raise(self, event_data: typing.Dict[str, typing.Any]) -> Route:
        for route in self.match(event_data):
            return route

        raise RouteNotFoundRouterError(self, event_data)

class RouterError(BaseException):
    def __init__(self, router: Router) -> None:
        super(RouterError, self).__init__()

        self.router = router

class RouteNotFoundRouterError(RouterError):
    def __init__(self, router: Router, event_data: typing.Dict[str, typing.Any]) -> None:
        super(RouteNotFoundRouterError, self).__init__(router)

        self.event_data = event_data

    def __str__(self) -> str: # pragma: no cover
        return 'route not found'

__all__ = ['Route', 'Router', 'RouterError', 'RouteNotFoundRouterError']
