#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

import json

class ResultsIterator():
    def __init__(self):
        self.current = -1
    def __iter__(self):
        return self
    def value_ok(self, _value):  
        return True
    def get_value(self, value):
        return value
    def __next__(self):
        self.current += 1
        while self.current < len(self.values):
            value = self.values[self.current]
            if not self.value_ok(value):
                self.current += 1
                continue
            return self.get_value(value)
        raise StopIteration


class ResultsIteratorForDockerCompose(ResultsIterator):
    BRANCH = 'dev'
    def __init__(self, values):
        super(ResultsIteratorForDockerCompose, self).__init__()
        self.values = json.loads(values)
    def value_ok(self, value):
        return value["Tag"] == ResultsIteratorForDockerCompose.BRANCH
#    def get_value(self, value):
#        return value['Repository'] + ':' + value['Tag']


class ResultsIteratorForText(ResultsIterator):
    def __init__(self, values):
        super(ResultsIteratorForText, self).__init__()
        self.values = values.splitlines()
    def value_ok(self, value):
        return len(value) > 0
