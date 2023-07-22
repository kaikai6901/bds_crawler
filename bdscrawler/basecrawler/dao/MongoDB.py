from pymongo import MongoClient
from bdscrawler.bdscrawler.settings import CONFIG_PATH, MONGO_CONFIG_NAME
from bdscrawler.basecrawler.dao.BaseDAO import BaseDAO
import configparser

class MongoDB(BaseDAO):
    def __int__(self):
        super(MongoDB, self).__int__()
        self.name = 'MongoDB'

    def read_config(self, config_path=CONFIG_PATH):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def connect(self):
        # host = self.config.get(MONGO_CONFIG_NAME, 'local_bind_host')
        # port = self.config.getint(MONGO_CONFIG_NAME, 'local_bind_port')
        username = self.config.get(MONGO_CONFIG_NAME, 'username')
        password = self.config.get(MONGO_CONFIG_NAME, 'password')
        # key_file = self.config.get(MONGO_CONFIG_NAME, 'key_file')

        try:
            # conn_str = f"mongodb://{username}:{password}@{host}:{port}/?directConnection=true&tls=true&tlsAllowInvalidHostnames=true&tlsCAFile={key_file}"
            # conn_str = f"mongodb://{username}:{password}@{host}:{port}/?directConnection=true"
            conn_str = f"mongodb+srv://{username}:{password}@hust.gfy8kif.mongodb.net/?retryWrites=true&w=majority"
            self.client = MongoClient(conn_str)
            self.test_connection()
        except Exception as e:
            raise Exception("Failed to connect to MongoDB: " + str(e))

    def test_connection(self):
        self.client.server_info()

    def get_client(self):
        if not self.client:
            self.read_config()
            self.connect()

        try:
            self.test_connection()
        except:
            print('Reconnecting to MongoDB')
            self.connect()

        return self.client
