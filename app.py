import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from ecfr_client import ECFRClient
from vector_store import initialize_rag
from graph import create_rip_graph
from langchain_google_vertexai import VertexAI # Or Ollama/HuggingFace
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Setup ---
st.title("RIP: Regulatory Intelligence Platform")
law_text = ECFRClient.get_part_11_text()
retriever = initialize_rag(law_text)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash") # Setup MedGemma endpoint

graph = create_rip_graph(retriever, llm)

# --- UI ---
protocol_input = st.text_area("Paste Protocol Section Here:", height=200)

if st.button("Run Regulatory Audit"):
    with st.spinner("MedGemma is cross-examining protocol..."):
        result = graph.invoke({"protocol_text": protocol_input})
        st.subheader("FDA Compliance Findings")
        st.markdown(result["audit_results"])
        
        with st.expander("View Retrieved Regulations"):
            for reg in result["retrieved_regulations"]:
                st.info(reg)