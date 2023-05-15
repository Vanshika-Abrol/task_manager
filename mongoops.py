import pymongo
def mongo_initializer():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    return client
