#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_event_handlers.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import json
import os
import unittest

from cloudevents.constants import SPEC_VERSION
from cloudevents.model import Event

from pacifica.notifications.client.event_handlers import NoopEventHandler

class NoopEventHandlerTestCase(unittest.TestCase):
    def test_event_handler(self):
        event = Event({
            'cloudEventsVersion': SPEC_VERSION,
            'eventID': '1',
            'eventType': 'example',
            'source': '/example',
            'data': [],
        })

        event_handler = NoopEventHandler()

        event_handler_return_value = event_handler.handle(event)

        self.assertEqual(None, event_handler_return_value)

        return

if __name__ == '__main__':
    unittest.main()
