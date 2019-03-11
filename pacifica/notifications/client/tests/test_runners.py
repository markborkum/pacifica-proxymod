#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_runners.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import os
import tempfile
import unittest

from ..downloader_runners import LocalDownloaderRunner
from ..models import File, Transaction, TransactionKeyValue
from ..uploader_runners import LocalUploaderRunner

class LocalRunnerTestCase(unittest.TestCase):
    def test_local_runners(self):
        transaction = Transaction(submitter=1, instrument=1, proposal=1)

        transaction_key_values = [
            TransactionKeyValue(key='Transactions._id', value=1),
        ]

        files = [
            File(name='filename.ext', subdir='filepath')
        ]

        file_strs = [
            'Hello, world!'
        ]

        self.assertEqual(len(files), len(file_strs))

        with tempfile.TemporaryDirectory() as basedir_name:
            for file, file_str in zip(files, file_strs):
                os.makedirs(os.path.join(basedir_name, os.path.dirname(file.path)))

                with open(os.path.join(basedir_name, file.path), mode='w') as f:
                    f.write(file_str)

                with open(os.path.join(basedir_name, file.path), mode='r') as f:
                    self.assertEqual(file_str, f.read())

            downloader_runner = LocalDownloaderRunner(basedir_name)

            with tempfile.TemporaryDirectory() as downloader_tempdir_name:
                openers = downloader_runner.download(downloader_tempdir_name, files=files)

                self.assertEqual(len(files), len(openers))

                with tempfile.TemporaryDirectory() as uploader_tempdir_name:
                    uploader_runner = LocalUploaderRunner()

                    for file, opener in zip(files, openers):
                        os.makedirs(os.path.join(uploader_tempdir_name, os.path.dirname(file.path)))

                        with opener() as orig_f:
                            with open(os.path.join(uploader_tempdir_name, file.path), mode='w') as new_f:
                                new_f.write(orig_f.read().upper())

                        with opener() as orig_f:
                            with open(os.path.join(uploader_tempdir_name, file.path), mode='r') as new_f:
                                self.assertEqual(orig_f.read().upper(), new_f.read())

                    (bundle, job_id, state) = uploader_runner.upload(uploader_tempdir_name, transaction=transaction, transaction_key_values=transaction_key_values)

                    self.assertTrue(bundle.md_obj.is_valid())

                    self.assertEqual(len(files), len(bundle.file_data))

                    for file, file_data in zip(files, bundle.file_data):
                        self.assertEqual(os.path.join('data', file.path), file_data.get('name', None))

                    self.assertEqual(None, job_id)
                    self.assertEqual({}, state)

        return

class RemoteRunnerTestCase(unittest.TestCase):
    def test_remote_runners(self):
        # TODO Auto-generated method stub.
        pass

if __name__ == '__main__':
    unittest.main()
