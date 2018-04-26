import yaml


class ConfigHandler:
    def __init__(self, cache=None):
        self.cache = cache

    def _fetch_config(self):
        if self.cache:
            if not self.cache.has('config'):
                with open('config.yml') as config:
                    settings = yaml.load(config)
                    self.cache.set('config', settings)
            return self.cache.get('config')
        else:
            with open('config.yml') as config:
                return yaml.load(config)

    def get(self, *keys):
        config = self._fetch_config()
        for key in keys:
            config = config[key]
        return config

    def has(self, *keys):
        config = self._fetch_config()
        for key in keys:
            if key not in config:
                return False
            config = config[key]
        return True
