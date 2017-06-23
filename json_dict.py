class jdict(dict):
    def __str__(self):
        return json.dumps(self)
