# -*- coding: utf-8 -*-
"""
This module provides user configuration file management features.

It's based on the ConfigParser module (present in the standard library).
"""

# Std imports
import ast
import os
import os.path as osp
import re
import shutil
import time
import configparser as cp

from typing import Iterator, Any, Dict, TypeVar, MutableSet

from packaging.version import Version

_DefaultsType = Dict[str, Dict[str, Any]]


class Config(cp.ConfigParser):
    def __init__(self, directory, name):
        cp.ConfigParser.__init__(self, interpolation=None)

        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created.")
        else:
            print(f"Directory '{directory}' already exists.")

        self.filename = os.path.join(directory, name)

        if os.path.exists(self.filename):  
            self.load(self.filename)
            #self.printConf()

    def printConf(self):
        for each_section in self.sections():
            print(each_section)
            for (each_key, each_val) in self.items(each_section):
                print(f'{each_key}: {each_val}')

    def get(self, section: str, option: str) -> Any:  
        raw_value: str = super().get(section, option, raw=True)
        return raw_value
        
    def set(self, section, option, value, verbose=False):
        if not self.has_section(section):
            self.add_section(section)
        if not isinstance(value, str):
            value = repr(value)
        if verbose:
            print('set: %s[ %s ] = %s' % (section, option, value))
        cp.ConfigParser.set(self, section, option, value)

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as configfile:
            self.write(configfile)

    def set_defaults(self, defaults):
        for section in defaults:
            for key, value in defaults[section].items():
                self.set(section, key, value, False)

    def load(self, filename):
        try:
            self.read(filename, encoding='utf-8')
        except cp.MissingSectionHeaderError:
            print("Warning: File contains no section headers.")


USER_DEFAULTS: _DefaultsType = {
    "Photo": {
        "path": "",  
    },
    "motor1": {
        "steppin": 0,
        "dirpin": 0,
        "ms1pin": 0,
        "ms2pin": 0,
        "ms3pin": 0,
        "step": 200,
        "maxSpeed": 400,
        "acceleration": 400,
        "speed": 400,
    },
    "motor2": {
        "steppin": 0,
        "dirpin": 0,
        "ms1pin": 0,
        "ms2pin": 0,
        "ms3pin": 0,
        "step": 200,
        "maxSpeed": 400,
        "acceleration": 400,
        "speed": 400,
    },
    "motor3": {
        "steppin": 0,
        "dirpin": 0,
        "ms1pin": 0,
        "ms2pin": 0,
        "ms3pin": 0,
        "step": 200,
        "maxSpeed": 400,
        "acceleration": 400,
        "speed": 400,
    },
    "sync": {
        "download": True,  # if upload sync is enabled
    },
}

class UserPreference(Config):
    def __init__(self, path, name):
        super().__init__(path, name)
        if not os.path.exists(self.filename):  
            self.set_defaults(USER_DEFAULTS)
        section = "Photo"
        key = "path"
        if not self.get(section, key):
            parent_dir = os.path.dirname(path)
            self.set(section, key, parent_dir, False)

    def test(self):
        pass
