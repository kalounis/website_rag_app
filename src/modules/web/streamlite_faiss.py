import os
import sys

import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from rag import RAGPipelineAPIFAISS


class StreamLiteAppAPIFAISS:
    def __init__(self, page_title: str, title: str, description: str, placeholder: str):
        self.rag = RAGPipelineAPIFAISS()
        self.page_title = page_title
        self.title = title
        self.description = description
        self.placeholder = placeholder
        self._configure_page()

    def _configure_page(self):
        st.set_page_config(page_title=self.page_title)
        st.title(self.title)
        st.markdown(self.description)

    def run(self):
        query = st.text_input("Your question:", placeholder=self.placeholder)
        if query:
            self._process_query(query)

    def _process_query(self, query: str):
        with st.spinner("Looking for the best answer, please wait..."):
            response, sources = self.rag.query(query)
            st.success("Answer:")
            st.markdown(response)
            st.markdown("---")
            if sources:
                st.caption("Sources used:")
                for src in sources:
                    st.markdown(f"- {src}")
            else:
                st.caption("No sources found.")
