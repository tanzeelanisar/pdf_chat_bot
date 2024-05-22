import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks, openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question, conversation_history):
    response = st.session_state.conversation({'question': user_question})

    # Check for duplicates before appending to conversation history
    new_messages = [message for message in response['chat_history'] if message not in conversation_history]
    conversation_history.extend(new_messages)

    for i, message in enumerate(new_messages):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="DocConverse")
    st.write(css, unsafe_allow_html=True)

    # Main content area
    st.markdown("<h1 style='text-align: center; color: white; padding: 10px; background-color: #002147;'>SmartDoc</h1>", unsafe_allow_html=True)
    st.markdown("---")  # Horizontal rule

    with st.sidebar:
        openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        st.markdown("Don't have an OpenAI API key? [Get it here](https://platform.openai.com/api-keys)")
        
        # Initialize chat_history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    uploaded_files = st.sidebar.file_uploader("Upload your PDF files", accept_multiple_files=True, type="pdf")

    if uploaded_files:
        process_files = st.sidebar.button("Process Uploaded Files")
        if process_files:
            progress_bar = st.sidebar.progress(0)
            progress_text = st.sidebar.empty()
            num_files = len(uploaded_files)
            for i, pdf_file in enumerate(uploaded_files, 1):
                progress_text.text(f"Processing file {i} of {num_files}")
                try:
                    get_pdf_text([pdf_file])
                except Exception as e:
                    st.error(f"An error occurred while processing {pdf_file.name}: {e}")
                progress_bar.progress(i / num_files)
                progress_text.text(f"Processed file {i} of {num_files}")

            text = ""
            for pdf_file in uploaded_files:
                text += get_pdf_text([pdf_file])
            text_chunks = get_text_chunks(text)
            vectorstore = get_vectorstore(text_chunks, openai_api_key)
            st.session_state.conversation = get_conversation_chain(vectorstore, openai_api_key)

    user_question = st.text_input("Enter your Prompt:",placeholder = "Ask a question about your documents:")

    if user_question:
        handle_userinput(user_question, st.session_state.chat_history)

    # Display conversation history with show/hide functionality
    with st.sidebar.expander("Conversation History", expanded=False):
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            if i % 2 == 0:
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)

if __name__ == '__main__':
    main()
