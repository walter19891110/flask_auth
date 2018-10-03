import psutil
import my_redis

redis_nodes = [{"host": "127.0.0.1", "port": "6379"},
               {"host": "127.0.0.1", "port": "6479"},
               {"host": "127.0.0.1", "port": "7379"},
               {"host": "127.0.0.1", "port": "7479"},
               {"host": "127.0.0.1", "port": "8379"},
               {"host": "127.0.0.1", "port": "8479"}
               ]

redis_cluster = my_redis.MyRedis(redis_nodes)

# 打印多网卡 mac 和 ip 信息
def PrintNetIfAddr():
    mac = '无 mac 地址'
    ipv4 = '无 ipv4 地址'
    dic = psutil.net_if_addrs()
    adapter = dic['en0']
    for snic in adapter:
        if snic.family.name in {'AF_LINK', 'AF_PACKET'}:
            mac = snic.address
        elif snic.family.name == 'AF_INET':
            ipv4 = snic.address

    print('%s, %s' % (mac, ipv4))


def test_redis():


if __name__ == "__main__":
    PrintNetIfAddr()