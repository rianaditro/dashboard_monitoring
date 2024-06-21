from extentions.get_data import Database

import streamlit as st


class AsrInput:
    def __init__(self, database: Database):
        self.asr_value = st.session_state['asr_value']
        self.database = database

    def update_asr(self):
        new_asr_value = st.session_state['asr_new_value']
        self.database.update_asr(new_asr_value)
        st.session_state['asr_value'] = new_asr_value

    def render(self):
        col1, col2 = st.columns((1,2))
        with col1:
            asr_input = st.number_input("Enter ASR value", 
                                    value=self.asr_value, 
                                    on_change=self.update_asr,
                                    key='asr_new_value', 
                                    )
        