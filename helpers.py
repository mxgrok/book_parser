

class ConfigStructure:

    def __init__(self, data: dict):
        self.__populate(data)

    def __populate(self, data: dict):
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
               setattr(
                   self, key, [ConfigStructure(item) if isinstance(item, dict) else item for item in value]
               )
            else:
               setattr(
                   self, key, ConfigStructure(value) if isinstance(value, dict) else value
               )

    def __getattr__(self, item):
        return
