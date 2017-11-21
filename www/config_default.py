#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

__author__ = 'lz'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'lizhi',
        'db': 'python_blog'
    },
    'session': {
        'secret': 'Awesome'
    }
}
