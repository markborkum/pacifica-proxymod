#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/downloader_runners.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import abc
import functools
import os
import typing

from pacifica.downloader import Downloader
from pacifica.notifications.client.models import File

def _to_opener(basedir_name: str, file: File) -> typing.Callable[[typing.Dict[str, typing.Any]], typing.TextIO]:
    func = lambda **kwargs: open(os.path.join(basedir_name, file.path), mode='r', encoding=file.encoding, **kwargs)

    return func

class DownloaderRunner(abc.ABC):
    def __init__(self) -> None:
        super(DownloaderRunner, self).__init__()

    @abc.abstractmethod
    def download(self, basedir_name: str, files: typing.List[File] = []) -> typing.List[typing.Callable[[typing.Dict[str, typing.Any]], typing.TextIO]]: # pragma: no cover
        raise NotImplementedError()

class LocalDownloaderRunner(DownloaderRunner):
    def __init__(self, basedir_name: str) -> None:
        super(LocalDownloaderRunner, self).__init__()

        self.basedir_name = basedir_name

    def download(self, basedir_name: str, files: typing.List[File] = []) -> typing.List[typing.Callable[[typing.Dict[str, typing.Any]], typing.TextIO]]:
        if self.basedir_name != basedir_name:
            for file in files:
                if file.subdir is not None:
                    os.makedirs(os.path.join(basedir_name, file.subdir), exist_ok=True)

                os.symlink(os.path.join(self.basedir_name, file.path), os.path.join(basedir_name, file.path))

        openers = list(map(functools.partial(_to_opener, basedir_name), files))

        return openers

class RemoteDownloaderRunner(DownloaderRunner):
    def __init__(self, downloader: Downloader) -> None:
        super(RemoteDownloaderRunner, self).__init__()

        self.downloader = downloader

    def download(self, basedir_name: str, files: typing.List[File] = []) -> typing.List[typing.Callable[[typing.Dict[str, typing.Any]], typing.TextIO]]:
        self.downloader._download_from_url(
            basedir_name,
            self.downloader.cart_api.wait_for_cart(
                self.downloader.cart_api.setup_cart(
                    map(lambda file: {
                        'id': file._id,
                        'hashsum': file.hashsum,
                        'hashtype': file.hashtype,
                        'path': file.path,
                    }, files)
                )
            ),
            'data'
        )

        openers = list(map(functools.partial(_to_opener, os.path.join(basedir_name, 'data')), files))

        return openers

__all__ = ['DownloaderRunner', 'LocalDownloaderRunner', 'RemoteDownloaderRunner']
