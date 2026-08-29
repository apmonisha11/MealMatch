import streamlit as st
from groq import Groq


@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def ask_food_bridge_ai(question):
    client = get_client()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.5,
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Food Bridge Assistant. Help users donate "
                    "surplus food safely, claim food, and understand "
                    "expiry times. Keep answers short and practical."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    return response.choices[0].message.content