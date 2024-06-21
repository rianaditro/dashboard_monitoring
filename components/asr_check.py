import streamlit as st
import pandas as pd


class AsrCheck:
    def __init__(self):
        self.asr_value = st.session_state['asr_value']

    def render(self, data: pd.DataFrame, is_disabled: bool = False):
        if is_disabled:
            st.checkbox('Tampilkan Data dibawah ASR', disabled=is_disabled, value=True)
            return data
        else:
            checkbox = st.checkbox('Tampilkan Data dibawah ASR', disabled=is_disabled)

            if checkbox:
                data = data[data['ASR(%)'] < self.asr_value]
                data = data[data['Calls'] > 0]
            return data
