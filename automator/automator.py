#!/usr/bin/env python3
# encoding: utf-8
import os

class Constants(object):
    ignored = ['.ds_store', 'secret.json']

    def __init__(self, arg):
        pass

class Automator(object):
    def __init__(self, target_file_path=None):
        self.base_path = self.get_base_path(target_file_path)
        self.secret = self._get_secret()

    @staticmethod
    def get_base_path(target_file_path=None):
        if target_file_path == None:
            target_file_path = os.path.abspath(__file__)

        return os.path.dirname(target_file_path)


    def _get_secret(self):
        import json

        with open(os.path.join(self.base_path, "SECRET.json")) as f:
            return json.load(f)
