#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_router.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import unittest

from jsonpath2.path import Path

from ..event_handlers import NoopEventHandler
from ..router import RouteNotFoundRouterError, Router

class RouterTestCase(unittest.TestCase):
    def test_blank_router_raises(self):
        router = Router()

        with self.assertRaises(RouteNotFoundRouterError):
            router(None)

    def test_router_matches(self):
        router = Router()

        router.add_route(Path.parse_str('$'), NoopEventHandler())

        self.assertEqual(1, len(list(router.match(None))))

if __name__ == '__main__':
    unittest.main()
