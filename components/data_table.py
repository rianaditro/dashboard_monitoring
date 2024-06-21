import streamlit as st
import pandas as pd

class DataTable:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.asr_value = st.session_state['asr_value']
    
    def styled_data(self):
        '''
        Below is the styling function for the data table
        '''
        def _highlight_asr(s,n):
            if s['ASR(%)'] < n and s['Calls'] > 0:
                return ['background-color: orange']*len(s)
            else:
                return ['background-color: white']*len(s)

        def _percentage(val):
            return f"{val:.2f}"

        def _format_arrow(val):
            return f"{'↑' if val > 0 else '↓'} {abs(val):.2f}" if val != 0 else f"{abs(val):.2f}"

        def _color_arrow(val):
            return "color: green" if val > 0 else "color: red" if val < 0 else "color: black"
        
        '''
        Styling function end here
        '''
        
        self.data = self.data.style.format(_percentage, subset=['ASR(%)', 'Prev ASR(%)']
                  ).format(_format_arrow, subset=['Difference']
                  ).map(_color_arrow, subset=['Difference'])
        
        self.data = self.data.apply(_highlight_asr, n=self.asr_value, axis=1)

        return st.dataframe(self.data, use_container_width=True)