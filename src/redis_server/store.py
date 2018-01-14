import threading
import time


class database:
    DATA = {}
    TTL = {}
    LOCK = threading.Lock()
    CONFIG = {"databases": "16"}

    @staticmethod
    def set(key, value):
        if database.LOCK.acquire():
            database.DATA[key] = value
            database.LOCK.release()

    @staticmethod
    def get(key):
        return database.DATA.get(key, None)

    @staticmethod
    def DEL(keys):
        ret = 0
        if database.LOCK.acquire():
            for key in keys:
                if database.DATA.get(key):
                    del database.DATA[key]
                    ret += 1
        database.LOCK.release()
        return ret

    @staticmethod
    def keys(key):
        ret = database.DATA.keys()
        return ret

    @staticmethod
    def get_type(key):
        return "string"

    @staticmethod
    def get_config(key):
        return [key, database.CONFIG.get(key, None)]

    @staticmethod
    def set_config(key, value):
        database.CONFIG[key] = value
        return "OK"

    @staticmethod
    def get_ttl(key):
        if database.get(key) is None:
            return -2
        ttl = database.TTL.get(key)
        if ttl:
            ttl = ttl - time.time()
            return int(ttl)
        return -1

    @staticmethod
    def expire(key, ttl):
        if database.LOCK.acquire():
            database.TTL[key] = time.time() + int(ttl)
        database.LOCK.release()
        return "OK"


def ttl_thread():
    while True:
        time.sleep(1)
        now = time.time()
        keys = database.TTL.keys()
        keys_to_del = []
        for key in keys:
            if now - database.TTL[key] >= 0:
                del database.TTL[key]
                keys_to_del.append(key)
        database.DEL(keys_to_del)


TTL_THREAD = threading.Thread(target=ttl_thread)
TTL_THREAD.start()