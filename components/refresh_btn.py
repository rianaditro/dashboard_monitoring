import streamlit as st

class RefreshBtn:
    def __init__(self):
        pass

    def refresh(self):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    def render(self):
        btn1, btn2 = st.columns((1,2))
        with btn1:
            refresh_btn = st.button("Refresh", type="primary")
            if refresh_btn:
                self.refresh()
