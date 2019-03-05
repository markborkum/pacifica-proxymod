#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_uploader_runners.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import os
import tempfile
import unittest

from pacifica.notifications.client.models import Transaction, TransactionKeyValue
from pacifica.notifications.client.uploader_runners import LocalUploaderRunner

class LocalUploaderRunnerTestCase(unittest.TestCase):
    def test_local_uploader_runner(self):
        with tempfile.TemporaryDirectory() as uploader_tempdir_name:
            os.makedirs(os.path.join(uploader_tempdir_name, 'filepath'))

            f_data = 'Hello, world!'

            with open(os.path.join(uploader_tempdir_name, 'filepath', 'filename.ext'), mode='w') as f:
                f.write(f_data)

            with open(os.path.join(uploader_tempdir_name, 'filepath', 'filename.ext'), mode='r') as f:
                self.assertEqual(f_data, f.read())

            uploader_runner = LocalUploaderRunner()

            (bundle, job_id, state) = uploader_runner.upload(uploader_tempdir_name, transaction=Transaction(submitter=1, instrument=1, proposal=1), transaction_key_values=[TransactionKeyValue(key='Transactions._id', value=1)])

            self.assertTrue(bundle.md_obj.is_valid())

            self.assertEqual(1, len(bundle.file_data))

            self.assertEqual(os.path.join('data', 'filepath', 'filename.ext'), bundle.file_data[0].get('name', None))

            self.assertEqual(None, job_id)
            self.assertEqual({}, state)

        return

class RemoteUploaderRunnerTestCase(unittest.TestCase):
    def test_remote_uploader_runner(self):
        # TODO Auto-generated method stub.
        pass

if __name__ == '__main__':
    unittest.main()
