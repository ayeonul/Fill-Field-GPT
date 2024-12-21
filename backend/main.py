import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from utils import *

import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))

# with open(
#     "./saved_engines/KoSimCSE-roberta-multitask/comp_unit_search3.pickle", "rb"
# ) as f:
#     search_unit = pickle.load(f)

app = FastAPI()
origins = [
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatbotPayload(BaseModel):
    messages: list
    user_status: dict


@app.post("/api/chat")
async def api_chat(payload: ChatbotPayload):
    chat_res, func_name, args = chat_engine(payload.messages, payload.user_status)
    return {"chat_res": chat_res, "func_name": func_name, "args": args}


@app.post("/api/greeting")
async def api_greeting():
    chat_res = greeting()
    return chat_res


async def main():
    config = uvicorn.Config("main:app", host="0.0.0.0", port=PORT, log_level="info")
    MAIN = uvicorn.Server(config)
    await MAIN.serve()


if __name__ == "__main__":
    asyncio.run(main())
