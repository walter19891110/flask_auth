import rediscluster


class MyRedis(object):

    def __init__(self, redis_nodes):
        self.r = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes)

    def set(self, key, value, ex):
        self.r.set(key, value, ex)

    def get(self, key):
        return self.r.get(key)