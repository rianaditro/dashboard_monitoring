from io import BytesIO


import streamlit as st
import pandas as pd


class DownloadBtn:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def render(self):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            self.data.to_excel(writer, index=False)

        st.download_button(label="Download", 
                        type='primary', 
                        data=buffer.getvalue(), 
                        mime='application/vnd.ms-excel',
                        key="download_excel_key")
