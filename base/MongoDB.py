from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://BaseKM:C1kb4PxHDnXu5WGd@cluster1.cmfubru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"


client = MongoClient(uri, server_api=ServerApi('1'))


try:
    client.admin.command('ping')
    print("Se hizo ping a tu implementación. Te conectaste correctamente a MongoDB!")
except Exception as e:
    print(e)