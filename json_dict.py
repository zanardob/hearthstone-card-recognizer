# This file simply changes the way the JSON handler prints dicts as strings, using double quotes instead of single quotes.

class jdict(dict):
    def __str__(self):
        return json.dumps(self)
