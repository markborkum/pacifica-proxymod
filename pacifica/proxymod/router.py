#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/proxymod/router.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import os

from jsonpath2.path import Path

from pacifica.notifications.client.downloader_runners import LocalDownloaderRunner
from pacifica.notifications.client.uploader_runners import LocalUploaderRunner
from pacifica.notifications.server.router import Router
from pacifica.proxymod.event_handlers import ProxEventHandler

# TODO Should be `RemoteDownloaderRunner(pacifica.downloader.Downloader(...))`.
downloader_runner = LocalDownloaderRunner(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test_files', 'C234-1234-1234', 'data')))

# TODO Should be `RemoteUploaderRunner(pacifica.uploader.Uploader(...))`.
uploader_runner = LocalUploaderRunner()

router = Router()

router.add_route(Path.parse_file(os.path.join(os.path.dirname(__file__), 'jsonpath2', 'proxymod.txt')), ProxEventHandler(downloader_runner, uploader_runner))

__all__ = ['router']
