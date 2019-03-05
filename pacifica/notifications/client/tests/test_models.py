#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_models.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import os
import unittest

from cloudevents.constants import SPEC_VERSION
from cloudevents.model import Event

from pacifica.notifications.client.exceptions import InvalidEventTypeValueError, InvalidSourceValueError, TransactionDuplicateAttributeError
from pacifica.notifications.client.globals import CLOUDEVENTS_DEFAULT_EVENT_TYPE_, CLOUDEVENTS_DEFAULT_SOURCE_
from pacifica.notifications.client.models import File, Transaction, TransactionKeyValue

class PacificaModelTestCase(unittest.TestCase):
    def setUp(self):
        self._file_data = {
            'destinationTable': 'Files',
            '_id': 1,
            'name': 'filename.ext',
            'subdir': 'filepath',
        }

        self._transaction_id_data = {
            'destinationTable': 'Transactions._id',
            'value': 1,
        }

        self._transaction_key_value_data = {
            'destinationTable': 'TransactionKeyValue',
            'key': 'key',
            'value': 'value',
        }

        self._event_data = []
        self._event_data.append(self._file_data)
        self._event_data.append(self._transaction_id_data)
        self._event_data.append(self._transaction_key_value_data)

        self._event_ok = Event({
            'cloudEventsVersion': SPEC_VERSION,
            'eventID': '1',
            'eventType': CLOUDEVENTS_DEFAULT_EVENT_TYPE_,
            'source': CLOUDEVENTS_DEFAULT_SOURCE_,
            'data': self._event_data,
        })

        self._event_error_invalid_event_type = Event({
            'cloudEventsVersion': SPEC_VERSION,
            'eventID': '1',
            'eventType': 'INVALID',
            'source': CLOUDEVENTS_DEFAULT_SOURCE_,
            'data': self._event_data,
        })

        self._event_error_invalid_source = Event({
            'cloudEventsVersion': SPEC_VERSION,
            'eventID': '1',
            'eventType': CLOUDEVENTS_DEFAULT_EVENT_TYPE_,
            'source': 'INVALID',
            'data': self._event_data,
        })

        self._event_data_error_duplicated_attr = self._event_data.copy()
        self._event_data_error_duplicated_attr.append(self._transaction_id_data)
        self._event_error_duplicated_attr = Event({
            'cloudEventsVersion': SPEC_VERSION,
            'eventID': '1',
            'eventType': CLOUDEVENTS_DEFAULT_EVENT_TYPE_,
            'source': CLOUDEVENTS_DEFAULT_SOURCE_,
            'data': self._event_data_error_duplicated_attr,
        })

        return

    def test_file_from_cloudevents_model_ok(self):
        inst_list = File.from_cloudevents_model(self._event_ok)

        self.assertEqual(1, len(inst_list))

        for name in ['_id', 'name', 'subdir']:
            self.assertEqual(self._file_data.get(name, None), getattr(inst_list[0], name, None))

        return

    def test_file_from_cloudevents_model_error_invalid_event_type(self):
        with self.assertRaises(InvalidEventTypeValueError):
            inst_list = File.from_cloudevents_model(self._event_error_invalid_event_type)

        return

    def test_file_from_cloudevents_model_error_invalid_source(self):
        with self.assertRaises(InvalidSourceValueError):
            inst_list = File.from_cloudevents_model(self._event_error_invalid_source)

        return

    def test_file_path_error(self):
        inst = File()

        with self.assertRaises(AttributeError):
            path = inst.path

        return

    def test_file_path_ok_name(self):
        inst = File(name=self._file_data.get('name', None))

        self.assertEqual(self._file_data.get('name', None), inst.path)

        return

    def test_file_path_ok_name_subdir(self):
        inst = File(name=self._file_data.get('name', None), subdir=self._file_data.get('subdir', None))

        self.assertEqual(os.path.join(self._file_data.get('subdir', None), self._file_data.get('name', None)), inst.path)

        return

    def test_transaction_from_cloudevents_model_ok(self):
        inst = Transaction.from_cloudevents_model(self._event_ok)

        self.assertEqual(self._transaction_id_data.get('value', None), inst._id)

        return

    def test_transaction_from_cloudevents_model_error_duplicated_attr(self):
        with self.assertRaises(TransactionDuplicateAttributeError):
            inst_list = Transaction.from_cloudevents_model(self._event_error_duplicated_attr)

        return

    def test_transaction_from_cloudevents_model_error_invalid_event_type(self):
        with self.assertRaises(InvalidEventTypeValueError):
            inst_list = Transaction.from_cloudevents_model(self._event_error_invalid_event_type)

        return

    def test_transaction_from_cloudevents_model_error_invalid_source(self):
        with self.assertRaises(InvalidSourceValueError):
            inst_list = Transaction.from_cloudevents_model(self._event_error_invalid_source)

        return

    def test_transaction_key_value_from_cloudevents_model_ok(self):
        inst_list = TransactionKeyValue.from_cloudevents_model(self._event_ok)

        self.assertEqual(1, len(inst_list))

        for name in ['key', 'value']:
            self.assertEqual(self._transaction_key_value_data.get(name, None), getattr(inst_list[0], name, None))

        return

    def test_transaction_key_value_from_cloudevents_model_error_invalid_event_type(self):
        with self.assertRaises(InvalidEventTypeValueError):
            inst_list = TransactionKeyValue.from_cloudevents_model(self._event_error_invalid_event_type)

        return

    def test_transaction_key_value_from_cloudevents_model_error_invalid_source(self):
        with self.assertRaises(InvalidSourceValueError):
            inst_list = TransactionKeyValue.from_cloudevents_model(self._event_error_invalid_source)

        return

if __name__ == '__main__':
    unittest.main()
