import chromadb
import datetime
import numpy as np

client = chromadb.Client()

collection = client.get_or_create_collection("test_random_online_no_virus_pls")


collection.add(ids=["1","2","3"], embeddings=np.random.uniform(-1, 1, (3, 384)),metadatas=[
    {"date":int(datetime.datetime.strptime("2024-08-20 14:30:00", "%Y-%m-%d %H:%M:%S").timestamp())},
    {"date":int(datetime.datetime.strptime("2023-08-20 14:30:00", "%Y-%m-%d %H:%M:%S").timestamp())},
    {"date":int(datetime.datetime.strptime("2022-08-20 14:30:00", "%Y-%m-%d %H:%M:%S").timestamp())},
])

results = collection.get(where={"date": {"$gt": int(datetime.datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())}})
print(results)
assert results["ids"] == ["1"]