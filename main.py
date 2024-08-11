import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# .env 파일 로드
load_dotenv()

def print_messages():
    """이전 대화기록 출력"""
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        for chat_message in st.session_state["messages"]:
            st.chat_message(chat_message.role).write(chat_message.content)
        
# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))

st.title("기술 질문")

# sesssion_state 초기화
if "messages" not in st.session_state:
    # 대화기록 저장
    st.session_state["messages"] = []

# 채팅 대화기록을 저장
if "store" not in st.session_state:
    st.session_state["store"] = dict()
    
# 세션 ID를 기반으로 세션 기록을 가져오는 함수 - 휘발성(메모리에 저장)
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]: #세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        st.session_state["store"][session_id] = ChatMessageHistory()
    return st.session_state["store"][session_id] # 해당 세션 ID에 대한 세션 기록 반환

# 이전 대화기록 출력
print_messages()

# 사용자 입력
if user_input := st.chat_input("메세지를 입력해주세요."):
    st.chat_message("user").write(user_input)
    add_message("user", user_input)
    
    # 프롬프트 생성
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "질문에 답변해 주세요."
            ),
            # 대화 기록을 저장 변수 이름: history
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"), # 사용자 질문 입력
        ]
    )
    
    # Chat모델
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # StrOutputParser: 모델의 출력을 문자열 형태로 파싱하여 반환
    chain = prompt | llm
    # response = chain.invoke({"question": user_input})
    
    chain_with_runnable = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question", # 사용자 질문
            history_messages_key="history", # 기록 메시지
        )

    response = chain_with_runnable.invoke(
        {"question": user_input},
        config={"configurable": {"session_id": "abc"}},
    )
    msg = response.content
    
    with st.chat_message("assistant"):
        st.write(msg)
    add_message("assistant", msg)