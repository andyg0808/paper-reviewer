import redis
import pickle


class Datastore:
    def __init__(self):
        self.db = redis.StrictRedis()

    def set(self, key, value):
        return self.db.set(key, value)

    def get(self, key):
        return self.db.get(key)

    def geti(self, key):
        stored = self.db.get(key)
        return int(stored)

    def has(self, key):
        return self.db.exists(key)

    def incr(self, key):
        return self.db.incr(key)

    def push(self, key, *value):
        return self.db.rpush(key, *value)

    def pop(self, key):
        return self.db.lpop(key)

    def llen(self, key):
        return self.db.llen(key)

    def getl(self, key, length):
        return self.db.lrange(key, 0, length)

    def delete(self, key):
        return self.db.delete(key)


class PickledDatastore(Datastore):
    def __init__(self, datastore):
        self.db = datastore.db

    def set(self, key, value):
        value = pickle.dumps(value)
        return self.db.set(key, value)

    def get(self, key):
        stored = self.db.get(key)
        return pickle.loads(stored)
