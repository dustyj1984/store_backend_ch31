import pymongo
import certifi

con_str = "mongodb+srv://dustyj1984:Team2022@cluster0.qblxpsa.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(con_str, tlsCAFile=certifi.where())

db = client.get_database("softx")


me = {
    "first_name": "Dustin",
    "last_name": "Jensen",
    "age": "18",
}

def hello():
    print("Hello there")