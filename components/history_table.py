import streamlit as st
import pandas as pd


class HistoryTable:
    def __init__(self, data: pd.DataFrame):
        self.display_data = self.styled_data(data)

    def styled_data(self, data: pd.DataFrame):
        '''
        Below is the styling function for the data table
        '''
        def _format_arrow(val):
            if val == "Updated":
                icon = "✅"
            elif val == "Not Up to Date":
                icon = "⚠️"
            else:
                icon = "❌"
            return f"{icon} {val}"

        def _color_arrow(val):
            if val == "Updated":
                return "color: green"
            elif val == "Not Up to Date":
                return "color: orange"
            else:
                return "color: red"
        '''
        Styling function end here
        '''

        data = data.style.format(_format_arrow, subset=['Status']
                                           ).map(_color_arrow, subset=['Status'])

        return st.dataframe(data, use_container_width=True)
