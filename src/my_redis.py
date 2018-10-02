import rediscluster
import sys


class MyRedis(object):

    def __init__(self, redis_nodes):
        self.r = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes)

    def connect_redis(self, redis_nodes):
        try:
            self.r = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes)
        except Exception as e:
            print('Connect Error!')
            sys.exit(1)

    def set(self, key, value, ex):
        self.r.set(key, value, ex)

    def get(self, key):
        return self.r.get(key)