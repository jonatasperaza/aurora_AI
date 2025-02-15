import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import DirectoryLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
import os

# Carrega variáveis de ambiente e chaves de acesso.
_ = load_dotenv(find_dotenv())

# Configura o servidor e o modelo local
ollama_server_url = "http://127.0.0.1:11434"
model_local = ChatOllama(model="llama3.1:1.5b-instruct-q4_K_S")

@st.cache_data
def load_markdown_data():
    # Verifica se já existe um índice FAISS salvo
    if os.path.exists("faiss_index"):
        with st.spinner("Carregando base de conhecimento do cache..."):
            vectorstore = FAISS.load_local("faiss_index", OllamaEmbeddings(
                base_url=ollama_server_url,
                model='nomic-embed-text'
            ))
            retriever = vectorstore.as_retriever()
            st.success("Base de conhecimento carregada com sucesso!")
            return retriever
    
    # Se não existir, cria um novo
    with st.spinner("Carregando e processando documentos... Isso pode demorar alguns minutos na primeira execução."):
        loader = DirectoryLoader("arquivos", glob="**/*.md")
        documents = loader.load()
        
        st.info(f"Carregados {len(documents)} documentos. Gerando embeddings...")
        
        embeddings = OllamaEmbeddings(
            base_url=ollama_server_url,
            model='nomic-embed-text'
        )
        
        vectorstore = FAISS.from_documents(documents, embeddings)
        # Salva o índice para uso futuro
        vectorstore.save_local("faiss_index")
        retriever = vectorstore.as_retriever()
        st.success("Base de conhecimento carregada com sucesso!")
        return retriever

# Carrega os dados
with st.spinner("Inicializando a aplicação..."):
    retriever = load_markdown_data()

st.title("Oráculo - Asimov Academy")

# Configuração do prompt e do modelo
rag_template = """
Você é um atendente de uma empresa.
Seu trabalho é conversar com os clientes, consultando a base de 
conhecimentos da empresa, e dar 
uma resposta simples e precisa para ele, baseada na 
base de dados da empresa fornecida como 
contexto.

Contexto: {context}

Pergunta do cliente: {question}
"""
human = "{text}"
prompt = ChatPromptTemplate.from_template(rag_template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model_local
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de entrada para o usuário
if user_input := st.chat_input("Você:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Adiciona um container para a resposta do modelo
    with st.spinner("Processando sua pergunta..."):
        response_stream = chain.stream(user_input)
        full_response = ""
        
        response_container = st.chat_message("assistant")
        response_text = response_container.empty()
        
        for partial_response in response_stream:
            content = partial_response.content if hasattr(partial_response, 'content') else str(partial_response)
            full_response += content
            response_text.markdown(full_response + "▌")
        
        # Remove o cursor no final
        response_text.markdown(full_response)

    # Salva a resposta completa no histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})