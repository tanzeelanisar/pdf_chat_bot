import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template
import os

load_dotenv()

def process_uploaded_file(uploaded_file):
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return uploaded_file.name

def generate_answer(question, response_placeholder):
    if question and st.session_state.vector_index:
        vector_index = st.session_state.vector_index
        docs = vector_index.get_relevant_documents(question)

        # Generate answer
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """

        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5, google_api_key=st.session_state.google_api_key)
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        response_dict = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
        response = response_dict["output_text"]

        # Update response
        response_placeholder.write(user_template.replace("{{MSG}}", question), unsafe_allow_html=True)
        response_placeholder.write(bot_template.replace("{{MSG}}", response), unsafe_allow_html=True)

        # Add asked question and generated answer to history
        st.session_state.question_history.append((question, response))

# Initialize session state if not present
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False

if 'vector_index' not in st.session_state:
    st.session_state.vector_index = None

if 'upload_status' not in st.session_state:
    st.session_state.upload_status = "No document uploaded yet."

# Main content area
st.markdown("<h1 style='text-align: center; color: white; padding: 10px; background-color: #002147;'>SmartDoc</h1>", unsafe_allow_html=True)
st.markdown("---")

# Create sidebar for key input, file uploader, and question history
with st.sidebar:
    google_api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="google_api_key")
    st.markdown("Don't have a Gemini API key? [Get it here](https://aistudio.google.com/app/apikey))")
    uploaded_file = st.file_uploader("Upload your document (PDF)", type="pdf")

    # Question history expander
    with st.expander("Chat History"):
        for qa_pair in st.session_state.question_history:
            question, answer = qa_pair
            st.write(user_template.replace("{{MSG}}", question), unsafe_allow_html=True)
            st.write(bot_template.replace("{{MSG}}", answer), unsafe_allow_html=True)

if st.session_state.google_api_key:
    # Set Google API key
    genai.configure(api_key=st.session_state.google_api_key)
    st.write(css, unsafe_allow_html=True)

    if uploaded_file and not st.session_state.document_processed:
        st.session_state.upload_status = "Uploading document..."
        with st.spinner(st.session_state.upload_status):
            file_path = process_uploaded_file(uploaded_file)

            # Load and split text
            loader = PyPDFDirectoryLoader(os.path.dirname(file_path))
            data = loader.load_and_split()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
            context = "\n\n".join(str(p.page_content) for p in data)
            texts = text_splitter.split_text(context)

            # Create embeddings and vector store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=st.session_state.google_api_key)
            st.session_state.vector_index = FAISS.from_texts(texts, embeddings).as_retriever()
            st.session_state.document_processed = True
            st.session_state.upload_status = "Document processed successfully!"

# Display the question prompt if the document is ready
if st.session_state.document_processed:
    question_placeholder = st.empty()
    response_placeholder = st.empty()
    question = question_placeholder.text_input("Ask a question", key="question")
    if question:
        generate_answer(question, response_placeholder)
