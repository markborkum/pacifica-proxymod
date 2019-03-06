#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/client/uploader_runners.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

import abc
import os
import tempfile
import time
import typing

from pacifica.notifications.client.exceptions import TransactionDuplicateAttributeError
from pacifica.notifications.client.models import Transaction, TransactionKeyValue
from pacifica.uploader import Uploader
from pacifica.uploader.bundler import Bundler
from pacifica.uploader.metadata import MetaData, MetaObj

def _should_sleep(**kwargs: typing.Dict[str, typing.Any]) -> bool:
    for name in ['state', 'task', 'task_percent']:
        if name not in kwargs:
            raise ValueError('field \'{0}\' is not defined'.format(name.replace('\'', '\\\'')))

    if 'OK' != kwargs.get('state', None):
        return True
    elif 'ingest metadata' != kwargs.get('task', None):
        return True
    elif 100 != int(float(kwargs.get('task_percent', None))):
        return True
    else:
        return False

def _to_bundler(basedir_name: str, transaction: Transaction = None, transaction_key_values: typing.List[TransactionKeyValue] = [], subdir_name: str = 'data') -> Bundler:
    meta_data = _to_meta_data(transaction=transaction, transaction_key_values=transaction_key_values)

    file_data = _walk(basedir_name)

    bundler = Bundler(meta_data, file_data)

    return bundler

def _to_meta_data(transaction: Transaction = None, transaction_key_values: typing.List[TransactionKeyValue] = []) -> MetaData:
    meta_objs = []

    if transaction is not None:
        for name in ['_id']:
            value = getattr(transaction, name, None)

            if value is not None:
                raise TransactionDuplicateAttributeError(None, name)

        for name in ['analytical_tool', 'description', 'instrument', 'proposal', 'submitter', 'suspense_date']:
            value = getattr(transaction, name, None)

            if value is not None:
                meta_obj = MetaObj(destinationTable='Transactions.{0}'.format(name), value=value)

                meta_objs.append(meta_obj)

    for transaction_key_value in transaction_key_values:
        meta_obj = MetaObj(destinationTable='TransactionKeyValue', key=transaction_key_value.key, value=transaction_key_value.value)

        meta_objs.append(meta_obj)

    meta_data = MetaData(meta_objs)

    return meta_data

def _walk(basedir_name: str) -> typing.List[typing.Dict[str, typing.Any]]:
    accum_value = []

    for orig_walk_root, walk_dirs, file_names in os.walk(basedir_name):
        new_walk_root = orig_walk_root[(len(basedir_name) + 1):]

        for file_name in file_names:
            orig_path = os.path.join(orig_walk_root, file_name)
            new_path = os.path.join(new_walk_root, file_name)

            st = os.stat(orig_path)

            # NOTE Character encoding is undetermined.
            accum_value.append({
                'fileobj': open(orig_path, mode='r'),
                'name': os.path.join('data', new_path),
                'size': st.st_size,
                # NOTE Should the next line be uncommented?
                # 'ctime': st.st_ctime,
                'mtime': st.st_mtime,
            })

    return accum_value

class UploaderRunner(abc.ABC):
    def __init__(self):
        super(UploaderRunner, self).__init__()

    @abc.abstractmethod
    def upload(self, basedir_name: str, transaction: Transaction = None, transaction_key_values: typing.List[TransactionKeyValue] = []) -> typing.Tuple[Bundler, int, typing.Dict[str, typing.Any]]: # pragma: no cover
        raise NotImplementedError()

class LocalUploaderRunner(UploaderRunner):
    def __init__(self):
        super(LocalUploaderRunner, self).__init__()

    def upload(self, basedir_name: str, transaction: Transaction = None, transaction_key_values: typing.List[TransactionKeyValue] = []) -> typing.Tuple[Bundler, int, typing.Dict[str, typing.Any]]:
        bundler = _to_bundler(basedir_name, transaction=transaction, transaction_key_values=transaction_key_values)

        # NOTE Prevent "ResourceWarning: unclosed file" warnings.
        for file_data in bundler.file_data:
            file_descriptor = file_data.get('fileobj', None)

            if (file_descriptor is not None) and not file_descriptor.closed:
                file_descriptor.close()

        return (bundler, None, {})

class RemoteUploaderRunner(UploaderRunner):
    def __init__(self, uploader: Uploader):
        super(RemoteUploaderRunner, self).__init__()

        self.uploader = uploader

    def upload(self, basedir_name: str, transaction: Transaction = None, transaction_key_values: typing.List[TransactionKeyValue] = []) -> typing.Tuple[Bundler, int, typing.Dict[str, typing.Any]]:
        bundler = _to_bundler(basedir_name, transaction=transaction, transaction_key_values=transaction_key_values)

        try:
            bundler_file = tempfile.NamedTemporaryFile(delete=False)
            bundler.stream(bundler_file)
            bundler_file.close()

            with open(bundler_file.name, mode='r') as bundler_file_descriptor:
                job_id = self.uploader.upload(bundler_file_descriptor, content_length=os.stat(bundler_file.name).st_size)

            state = self.uploader.getstate(job_id)

            while _should_sleep(**state):
                time.sleep(1)

                state = self.uploader.getstate(job_id)

            return (bundler, job_id, state)
        finally:
            os.unlink(bundler_file.name)

__all__ = ('UploaderRunner', 'LocalUploaderRunner', 'RemoteUploaderRunner')
