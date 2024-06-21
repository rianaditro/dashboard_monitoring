
from extentions.get_data import Database
from streamlit_navigation_bar import st_navbar

import pages as pg
import streamlit as st

st.set_page_config(page_title="Dashboard Monitoring", layout='wide', initial_sidebar_state='collapsed')

page = st_navbar(["Dashboard","Statistik GE", "Statistik 4 Modul", "Statistik 32 Modul", "Manajemen Perangkat"],
                 options={'show_menu':False, 'show_sidebar':False})

def main(database: Database):
    if page == "Dashboard":
        pg.home_page(database)
    if page == "Statistik GE":
        pg.ge_page(database)
    elif page == "Statistik 4 Modul":
        pg.vbm_page(database)
    elif page == "Statistik 32 Modul":
        pg.sg_page(database)
    elif page == "Manajemen Perangkat":
        pg.perangkat_page(database)

def check_asr(database: Database):
    if 'asr_value' not in st.session_state:
        asr_value = database.get_asr_from_db()
        st.session_state['asr_value'] = asr_value
    return st.session_state['asr_value']


if __name__ == "__main__":
    database = Database()

    check_asr(database)
    main(database)
    