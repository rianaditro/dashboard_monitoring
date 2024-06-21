from components import *
from extentions.get_data import Database

import streamlit as st
import streamlit_antd_components as sac
import pandas as pd



class ContainerTable:
    def __init__(self, title:str, database:Database):
        if title == 'VBM':
            table_data = database.get_vbm_data()
        elif title == 'SG':
            table_data = database.get_sg_data()
        elif title == 'GE':
            table_data = database.get_ge_data()
        else:
            table_data = database.get_home_data()

        self.title = title
        self.database = database
        self.table_data = table_data

    def split_data(self, dataframe:pd.DataFrame):
        # split one page for all the latest data
        # splited_data = [d for _, d in self.table_data.groupby(self.table_data['Upload ID'])][::-1]

        # splite data by 50 entry only
        splited_data = [d for _, d in dataframe.groupby(dataframe.index // 50)]
        return splited_data, len(splited_data)
    
    def render(self, asr_disabled: bool = False):
        # frontend section
        st.write("Tabel Terbaru")
        RefreshBtn().render()
        AsrInput(self.database).render()
        asr_check_data = AsrCheck().render(self.table_data, asr_disabled)
        splited_data, total_page = self.split_data(asr_check_data)

        pagination = sac.pagination(
            total=total_page,simple=True, 
            page_size=1, align="center")
        
        if total_page == 0:
            st.warning("Tidak ada data untuk ditampilkan.")
        else:
            DataTable(splited_data[pagination-1]).styled_data()

        DownloadBtn(self.table_data).render()

class ContainerUpload:
    def __init__(self, title:str):
        self.title = title

    def render(self):
        if self.title == 'VBM':
            tipe_perangkat = 'Perangkat 4 Modul'
        elif self.title == 'SG':
            tipe_perangkat = 'Perangkat 32 Modul'

        daftar_perangkat = self.database.filter_tipe_perangkat(self.perangkat_table, self.title)['Nama Perangkat']

        st.subheader("Upload File Statistik", anchor=False)
        col1, col2, col3 = st.columns(3)
        nama_perangkat_widget = col1.selectbox("Pilih Perangkat", daftar_perangkat)
        ip_selected_widget = col2.text_input("IP Perangkat", value=nama_perangkat_widget, disabled=True)
        col3.text_input('Tipe Perangkat', value=tipe_perangkat, disabled=True)
        uploader_widget = st.file_uploader("Pilih File Statistik", type='txt', accept_multiple_files=False)
 

class Page:
    def __init__(self, title:str, database:Database):
        self.title = title
        self.database = database

    def container_perangkat(self):
        data = self.database.perangkat_table
        
        st.subheader("Manajemen Perangkat", anchor=False)
        edit_table = st.data_editor(data=data,
                                    use_container_width=True,
                                    num_rows="dynamic",
                                    column_config={
                                        'Tipe Perangkat': st.column_config.SelectboxColumn(
                                            "Tipe Perangkat", 
                                            options=[
                                                'Perangkat 4 Modul',
                                                'Perangkat 32 Modul',
                                                'Perangkat GE'
                                            ]
                                        )
                                    })
        save_changes = st.button("Simpan Perubahan", type="primary")

        if save_changes:
            self.database.c.execute('DELETE FROM perangkat_table')
            for index, row in edit_table.iterrows():
                self.database.c.execute(f"INSERT INTO perangkat_table (nama_perangkat, ip_address, tipe_perangkat) VALUES (\'{row['Nama Perangkat']}\', \'{row['IP Address']}\', \'{row['Tipe Perangkat']}\')")
            self.database.conn.commit()

    def container_table(self, asr_disabled: bool = False):
        container_table = ContainerTable(self.title, self.database)
        with st.container(border=True):
            container_table.render(asr_disabled)
            
    def container_history(self):
        history_data = self.database.filter_tipe_perangkat(self.database.history_table, self.title)
        with st.container(border=True):
            st.subheader("Riwayat Upload", anchor=False)
            HistoryTable(history_data).display_data
    
    def container_upload(self):
        pass
   