

class Structure:

    def __init__(self, data: dict):
        self.__populate(data)

    def __populate(self, data: dict):
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
               setattr(
                   self, key, [Structure(x) if isinstance(x, dict) else x for x in value]
               )
            else:
               setattr(
                   self, key, Structure(value) if isinstance(value, dict) else value
               )

    def __getattr__(self, item):
        return
