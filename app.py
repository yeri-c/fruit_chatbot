# max_tokens=644, 온도, top-p, stop=None, frequency_penalty=0, presence_penalty=0
import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def my_chatbot(user_input, message_cnt=3, max_tokens=800, temperature=0.7, top_p=0.95, stop=None, frequency_penalty=0, presence_penalty=0):

    endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
    subscription_key = os.getenv("AZURE_OAI_KEY")

    message_limit = message_cnt * 2

    # Initialize Azure OpenAI client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2025-01-01-preview",
    )

    # Prepare the chat prompt
    chat_prompt = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "너는 과일전문가야. 사용자가 과일에 대해서 질문하면 맛과 영양성분 등에 대해서 귀여운 어투로 대답해줘. 답변의 길이는 200자 이내로"
                }
            ]
        }
    ]

    # session_state에서 대화 내역 불러오기 (while True 대체)
    for msg in st.session_state.messages:
        chat_prompt.append(msg)

    # 기존 대화 내역 갯수 제어
    if len(chat_prompt) > (1 + message_limit):
        chat_prompt = [chat_prompt[0]] + chat_prompt[-message_limit:]

    chat_prompt.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_input
            }
        ]
    })

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        stream=False
    )

    # AI의 답변을 처리
    ai_response = completion.choices[0].message.content

    return ai_response


# Streamlit UI (input/while True 대체)
st.title("🍓 과일 전문가 AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내역 출력
for msg in st.session_state.messages:
    role = "🙋 유저" if msg["role"] == "user" else "💬 과일 전문가"
    st.chat_message(msg["role"]).write(msg["content"][0]["text"])

# 사용자 입력
if user_input := st.chat_input("과일에 대해 질문해보세요!"):
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({
        "role": "user",
        "content": [{"type": "text", "text": user_input}]
    })

    ai_response = my_chatbot(user_input)

    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({
        "role": "assistant",
        "content": [{"type": "text", "text": ai_response}]
    })