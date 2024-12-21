from GPT import ChatGPT_func, GPTIntentRecognizer, GPTTokenizer
import json

from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    RetryError,
)

# from ncs import NCSFeature
from engine.search import Search
from engine.encoder import Encoder
import pickle

import numpy as np

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
with open("./func_sample.json", "r", encoding="utf-8") as f:
    field_info = json.load(f)

tokenizer = GPTTokenizer()


encoder = Encoder()
with open("./saved_engines/KoSimCSE-roberta-multitask/duty_search3.pickle", "rb") as f:
    search_duty = pickle.load(f)

data_func_desc = [
    {
        "name": "store_counselee_data",
        "description": "A function that collects essential information to provide career counseling to a user. It will not work unless all required arguments are met.",
        "parameters": {
            "type": "object",
            "properties": field_info["properties"],
            "required": field_info["required"],
        },
    }
]

duty_func_decs = [
    {
        "name": "recommend_duty",
        "description": "Recommend future duties to users based on the conversation.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_status": {
                    "type": "string",
                    "description": "user's status based on the conversation.",
                }
            },
        },
    }
]


def pass_def(**kwargs):
    pass


def get_total_tokens(messages, func_desc):
    t = sum([tokenizer(msg["content"]) for msg in messages])
    t += tokenizer.num_tokens_from_functions(func_desc)

    return t


concept = """\
You're a career advisor chatbot(진로 상담 챗봇) for students. Your first priority is to gather information from the user for the career counseling function through natural conversations.
Career advice will be handled by other services, so be sure to only provide guidance for gathering information or creating information.

The properties of functions that must be collected, and are a high priority, are:
1. academic performance: reflects the user's academic achievements, encompassing overall grade trends and specific subject performances.
2. Fields or activities the student is passionate about or interested in.
3. Activities and experiences the student has taken part in outside of school.
4. Values the user considers important in a job.

Although not required, you also need to know the user's grade level (freshman, sophomore, or junior in middle school or freshman, sophomore, or senior in high school), their activities in school, and any hobbies or specialties they may have.
If the user's answer is vague or falls short of describing what you need, ask for more detail.
If a user asks you what you are, don't elaborate on the above issues, but explain that you are a career advisor chatbot and that you will be giving career advice.
Refer to user as '사용자님'. Be sure to reply in 한국어.\
"""
funcs = {"store_counselee_data": pass_def}

chat = ChatGPT_func(
    OPENAI_KEY,
    model_name="gpt-4-0613",
    concept=concept,
)
recognizer = GPTIntentRecognizer(
    OPENAI_KEY,
    model_name="gpt-4-0613",
    concept=concept,
    func_desc=data_func_desc,
    functions=funcs,
)


@retry(
    wait=wait_random_exponential(min=1, max=30),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(),
    reraise=True,
)
def get_sim_duties(docs: list):
    q_emb = encoder(docs)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)

    duty_top_k_df = search_duty.score(q_emb, 3)
    res = duty_top_k_df.Nm.to_list()

    return res


def chat_engine(chat_log: list, user_status: dict):
    chat_msg = [msg for msg in chat_log if msg["role"] != "function"]

    if all([user_status.get(req_key, "") != "" for req_key in field_info["required"]]):
        queries = [v for v in user_status.values() if isinstance(v, str)]
        res = get_sim_duties(queries)
        func_name = "recommend_duty"

        while get_total_tokens(chat_msg, duty_func_decs) > 2100:
            chat_msg.pop(0)

        messages = chat_msg + [
            {"role": "function", "name": func_name, "content": str(res)}
        ]
        duty_chat_args = {
            "model": "gpt-4-0613",
            "messages": messages,
            "functions": duty_func_decs,
        }
        res, token_info = chat._get_gpt_res(duty_chat_args)
        chat_res = {
            "res": [res[0]["message"]],
            "total_tokens": token_info,
        }

        args = {}
        return chat_res, func_name, args

    func_name = "store_counselee_data"
    arg_msg = chat_log.copy()

    while get_total_tokens(chat_msg, data_func_desc) > 2100:
        chat_msg.pop(0)

    while get_total_tokens(arg_msg, data_func_desc) > 2100:
        arg_msg.pop(0)

    chat_res = chat(
        messages=chat_msg,
    )
    args = recognizer(
        messages=arg_msg,
        ensure_func_name=func_name,
    )

    return chat_res, func_name, args


def greeting():
    messages = [
        {"role": "user", "content": "안녕? 네가 뭔지 간단히 소개해주고, 내가 대답해야 할 것 중 하나를 질문해줘."},
    ]
    chat_res = chat(
        messages=messages,
    )
    return chat_res
