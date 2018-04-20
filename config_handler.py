import yaml


class ConfigHandler:
    def __init__(self, cache):
        self.cache = cache

    def get(self, key):
        if not self.cache.has('config'):
            with open('config.yml') as config:
                settings = yaml.load(config)
                self.cache.set('config', settings)
        config = self.cache.get('config')
        return config[key]
