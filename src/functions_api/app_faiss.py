import os
import sys

import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))
from web import StreamLiteAppAPIFAISS

if __name__ == "__main__":
    app = StreamLiteAppAPIFAISS(
        page_title=f"{st.secrets['COMPANY_NAME']} FAQ Assistant",
        title=f"{st.secrets['COMPANY_NAME']} - FAQ Assistant",
        description=f"Ask a question based on {st.secrets['COMPANY_NAME']} official help page.",
        placeholder="e.g., How do I set up voicemail?",
    )
    app.run()
