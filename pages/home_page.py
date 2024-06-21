from extentions.template import Page

import streamlit as st


def main_page(database):
    page = Page('homepage', database)

    # frontend section
    st.subheader(f"Statistik Tabel Summary", anchor=False)
    page.container_table(asr_disabled=True)