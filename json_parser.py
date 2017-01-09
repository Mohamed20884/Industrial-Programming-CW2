import json


class JsonParser():
    """
        Parses json into dictionary objects and stores them to an array
    """
    def __init__(self):
        self.d = []

    def add(self, item):
        self.d.append(json.loads(item))

    def get_all(self):
        return self.d
