class BaseDAO:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.name = None
        self.client = None
        self.config = None

    def read_config(self, config_path):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def test_connection(self):
        raise NotImplementedError

    def get_client(self):
        raise NotImplementedError