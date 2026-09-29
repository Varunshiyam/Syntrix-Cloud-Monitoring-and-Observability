from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
def test():
    raise Exception("DB failed")

client = TestClient(app)
print(client.get("/").text)
