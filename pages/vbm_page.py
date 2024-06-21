from extentions.template import Page

import streamlit as st


def main_page(database):
    page = Page('VBM', database)

    # frontend section
    st.subheader(f"Statistik Tabel Modul {page.title}", anchor=False)
    page.container_table()
    st.divider()
    page.container_history()