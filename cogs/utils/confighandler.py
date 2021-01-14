import json 

class CogConfigHandler:
    def __init__(self, jsonfile):
        self._jsonfile = jsonfile
        with open(jsonfile) as fp:
            self.jsodata = json.load(fp)

    def dump(self, **kwargs):
        with open(self._jsonfile, 'w') as fp:
            json.dump(self.jsodata, fp, indent=kwargs.pop('indent', 4), **kwargs)