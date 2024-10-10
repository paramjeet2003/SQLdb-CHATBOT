import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine ## to map the output coming from the sql database
import sqlite3
from langchain_groq import ChatGroq


st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

INJECTION_WARNING = """
SQL agent can be vulnerable to prompt injection, Use a DB role with limit.
"""
LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

## radio option
radio_opt = ["Use SQLLite 3 Databse - Student.db", "Connect to your SQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB, to chat with:", options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Hostname")
    mysql_user = st.sidebar.text_input("User")
    mysql_passwd = st.sidebar.text_input("Password", type="password")
    mysql_db = st.sidebar.text_input("Database")
else: 
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API key", type="password")

if not db_uri:
    st.info("Please enter the Database information and uri")

if not api_key:
    st.info("Please add the Groq API key")

## LLM model 
llm = ChatGroq(model="Llama3-8b-8192", groq_api_key=api_key, streaming=True)

## database connection
## to avoid login again and again
@st.cache_resource(ttl="2") ## till 3 hours keep it in the cache 
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_passwd=None, mysql_db=None, auth_plugin='mysql_native_password'):
    if db_uri==LOCALDB:
        db_filepath = (Path(__file__).parent/"student.db").absolute()
        print(db_filepath)
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_passwd and mysql_db):
            st.error("Please provide all MYSQL connection details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+pymysql://{mysql_user}:{mysql_passwd}@{mysql_host}/{mysql_db}"))
        ### since mysqlconnector has not worked, so i used pymysql
if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_passwd,mysql_db)
else:
    db = configure_db(db_uri)

## toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role":"assistant", "content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user", "content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant", "content":response})
        st.write(response)
