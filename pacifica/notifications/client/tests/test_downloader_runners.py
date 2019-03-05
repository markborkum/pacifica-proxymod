#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/tests/test_downloader_runners.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import os
import tempfile
import unittest

from pacifica.notifications.client.downloader_runners import LocalDownloaderRunner
from pacifica.notifications.client.models import File

class LocalDownloaderRunnerTestCase(unittest.TestCase):
    def test_local_downloader_runner(self):
        with tempfile.TemporaryDirectory() as basedir_name:
            os.makedirs(os.path.join(basedir_name, 'filepath'))

            f_data = 'Hello, world!'

            with open(os.path.join(basedir_name, 'filepath', 'filename.ext'), mode='w') as f:
                f.write(f_data)

            with open(os.path.join(basedir_name, 'filepath', 'filename.ext'), mode='r') as f:
                self.assertEqual(f_data, f.read())

            downloader_runner = LocalDownloaderRunner(basedir_name)

            with tempfile.TemporaryDirectory() as downloader_tempdir_name:
                openers = downloader_runner.download(downloader_tempdir_name, files=[File(name='filename.ext', subdir='filepath')])

                self.assertEqual(1, len(openers))
                with openers[0]() as f:
                    self.assertEqual(f_data, f.read())

        return

class RemoteDownloaderRunnerTestCase(unittest.TestCase):
    def test_remote_downloader_runner(self):
        # TODO Auto-generated method stub.
        pass

if __name__ == '__main__':
    unittest.main()
