from pymongo import MongoClient


class MongoDbClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDbClient, cls).__new__(cls)
            cls._instance._initialize_client(*args, **kwargs)
        return cls._instance

    def _initialize_client(self, uri="mongodb://root:root@mongodb:27017/", db_name="capstone_project_collection"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        print("MongoDB connection established.")

    def get_db(self):
        return self.db

    def close_connection(self):
        self.client.close()
        print("MongoDB connection closed.")