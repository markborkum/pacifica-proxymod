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

from pacifica.cli.methods import generate_global_config, generate_requests_auth
from pacifica.downloader import Downloader
from pacifica.notifications.client.downloader_runners import RemoteDownloaderRunner
from pacifica.notifications.client.router import Router
from pacifica.notifications.client.uploader_runners import RemoteUploaderRunner
from pacifica.proxymod.event_handlers import ProxEventHandler
from pacifica.uploader import Uploader

config = generate_global_config()

auth = generate_requests_auth(config)

downloader_runner = RemoteDownloaderRunner(Downloader(cart_api_url=config.get('endpoints', 'download_url'), auth=auth))

uploader_runner = RemoteUploaderRunner(Uploader(upload_url=config.get('endpoints', 'upload_url'), status_url=config.get('endpoints', 'upload_status_url'), auth=auth))

router = Router()

router.add_route(Path.parse_file(os.path.join(os.path.dirname(__file__), 'jsonpath2', 'proxymod.txt')), ProxEventHandler(downloader_runner, uploader_runner))

__all__ = ('router')
