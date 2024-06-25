from fastapi import FastAPI
from typing import Union
from redis import Redis
import httpx
import json

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(host="localhost", port=6379)
    app.state.http_client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()


@app.get("/entries")
async def entries_event():
    value = app.state.redis.get("entries")

    if value is None:
        response = await app.state.http_client.get("https://reqres.in/api/users")
        print(response)
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set("entries", data_str)
    return json.loads(value)
