#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pacifica-notifications-client: pacifica/notifications/server/config.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE and WARRANTY for details.

try:
    from ConfigParser import SafeConfigParser
except ImportError: # pragma: no cover python 2 vs 3 issue
    from configparser import SafeConfigParser

import os

def _strip(s: str) -> str:
    if s is None:
        return None

    for c in ["'", '"']:
        if s[0] == c:
            if s[-1] == c:
                # NOTE Strip leading and trailing quote characters and replace backslash-quoted quote characters.
                s = s[1:-1].replace('\\{0}'.format(c), c)
            else:
                raise ValueError('Expecting trailing quote character: {0}'.format(c))
        else:
            if s[-1] == c:
                raise ValueError('Expecting leading quote character: {0}'.format(c))
            else:
                pass

    # NOTE Strip trailing and leading whitespace characters.
    return s.strip()

def get_config(path: str) -> SafeConfigParser:
    safe_config_parser = SafeConfigParser()

    safe_config_parser['database'] = {
        'peewee_url': 'sqliteext:///db.sqlite3',
    }

    safe_config_parser.read(path)

    safe_config_parser.set('database', 'peewee_url', _strip(safe_config_parser.get('database', 'peewee_url')))

    return safe_config_parser

def get_config_file_path(key: str = 'PACIFICA_NOTIFICATIONS_SERVER_CONFIG', dirname: str = '.pacifica-notifications-server', basename: str = 'config.ini') -> str:
    return os.getenv(key, os.path.join(os.path.expanduser('~'), dirname, basename))

__all__ = ['get_config', 'get_config_file_path']
