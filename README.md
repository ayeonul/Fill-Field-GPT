# chat-based-field-assistant

## Project setup

```bash
node -v
# 18.12.1

# 최초 1회
npm install
conda create -f requirements.yaml

conda activate chat
```

## Run backend (use hot-reload)

```bash
cd backend

uvicorn main:app --port 5000 --reload
# run on localhost:5000
# for more documentation, visit localhost:5000/docs.
```

## Run frontend (on dev server, use hot-reload)

```bash
npm run serve
# run on localhost:8080
```

<br/>

## 그래서 이게 뭐하는 앤가요?

* GPT와 대화를 통해 사용자의 여러 정보를 취득하고, 취득한 정보를 통해 NCS 직무를 추천하는 `진로 상담 챗봇`

## UI 설명 좀

* 챗봇이 첫 인사말을 출력한 뒤 화면 하단 채팅창을 통해 대화를 나눌 수 있습니다.
* 대화를 나누면 챗봇의 각 응답 바로 밑에 검은색 바탕의 흰 _obj(dict)_ 가 같이 출력되는데, 이게 사용자의 대답을 통해 추출된 정보입니다.
* 추출된 정보는 화면 왼쪽 하단 `현재 정보` 칸에 update됩니다.
* 화면 왼쪽의 `대화내역 다운로드`, `대화내역 업로드` 버튼을 통해 이때까지의 대화내역을 json file로 다운로드 받거나, 업로드 후 대화를 이어나갈 수 있습니다. 단, 챗봇이 응답 중일 땐 버튼이 동작하지 않습니다.

## 동작 과정 설명 좀

* 여기엔 총 2개의 GPT가 사용되는데, 사용자와 직접 대화를 나누는 GPT(이하 `대화 GPT`)와 function call 기능을 이용해 대화 로그에서 정보를 취득하는 GPT(이하 `정보 취득 GPT`)가 있습니다.

1. greeting api(여기엔 GPT에게 _너 자신을 소개하고 사용자가 어떤 걸 답해줘야 하는지 말해라_ 라는 프롬프트에 대한 답이 옵니다)를 통해 사용자에게 먼저 질문합니다.
2. 사용자가 그에 대한 대답을 합니다.
3. 대화 GPT의 system prompt에는 챗봇이 필수적으로 모아야 할 사용자 정보에 대한 설명과 부가적으로 모으면 좋을 정보에 대한 설명이 있고, 최우선 과제가 위의 정보들을 취득하는 것이라고 해둔 상태입니다. 대화 GPT는 위의 필수 정보를 모으기 위해 다시 사용자와의 _대화만을_ 이어갑니다. `매끄러운 대화를 위해, 대화 GPT는 정보를 취득하지 않습니다.`
4. `/backend/func_sample.json` 파일에도 챗봇이 모아야 할 사용자 정보에 대한 설명이 적혀있습니다. 대화 GPT가 정보를 모으지 않는 대신, 정보 취득 GPT가 이 파일의 내용을 통해 대화 로그에서 샤용자 정보를 취득합니다.
5. 3번 과정으로 대화 GPT에서 나온 응답과 4번 과정으로 정보 취득 GPT에서 추출한 정보를 함께 FE에 반환합니다.
6. FE는 대화 GPT의 응답을 챗봇 응답으로서 저장 및 출력하고, 정보 취득 GPT에서 추출한 정보를 사용자 정보에 update합니다.
7. greeting api call을 제외한 위 과정을 반복합니다.
8. `/backend/func_sample.json` 파일에 선언된 필수 정보들이 모두 채워지면, 이 정보값들만을 모아 embedding을 구하고 각 NCS 세분류와 유사도를 구해 최고 유사도의 직무 3개를 산출, 대화 GPT에게 직무 추천 함수의 결과값이랍시고 prompt에 추가해서 입력합니다.
9. 대화 GPT가 이때까지 대화 흐름에 맞게 추천 직무에 대해 잘 설명해줍니다!
