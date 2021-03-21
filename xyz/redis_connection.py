import redis


class RedisConnection:

    redis_server_parameters = None
    redis_conn_pool = None

    @classmethod
    def setup_conn_pool(cls, *, server_params: dict, max_conn: int):
        cls.redis_server_parameters = server_params
        cls.redis_pool = redis.ConnectionPool(**cls.redis_server_parameters, max_connections=max_conn)

    def __init__(self, *, redis_server_params: dict = {"host": "localhost", "port": 6379, "db": 0}, max_conn: int = 99):
        if self.redis_conn_pool is None:
            self.setup_conn_pool(server_params=redis_server_params, max_conn=max_conn)
        self.redis_connection = redis.StrictRedis(connection_pool=self.redis_conn_pool)

    def get_connection(self):
        return self.redis_connection


if __name__ == "__main__":
    r = RedisConnection()
    r_conn = r.get_connection()
    r_conn.lpush("LIST1", *["a", "b"])
    while popped_elem := r_conn.lpop("LIST1"):
        print(popped_elem.decode("utf-8"))
    else:
        print("Else-block with popped_elem equals to:", popped_elem)
