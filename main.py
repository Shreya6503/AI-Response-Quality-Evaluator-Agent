import streamlit as st

pages = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/evaluation_hub.py", title="Evaluation Hub", icon="🧪"),
]

page = st.navigation(pages, position="hidden")
page.run()
