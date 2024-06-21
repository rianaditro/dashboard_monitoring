from extentions.get_data import Database
from extentions.extractor import Extractor
from io import StringIO

import pandas as pd
import streamlit as st



class UploadForm:
    def __init__(self, module:str, database: Database):
        self.module = module
        self.database = database
        self.daftar_perangkat,  self.daftar_ip_perangkat = self.get_daftar_perangkat()

    def get_daftar_perangkat(self):
        perangkat_table = self.database.perangkat_table
        perangkat_table = self.database.filter_tipe_perangkat(
            perangkat_table, self.module)
        daftar_nama_perangkat = perangkat_table['Nama Perangkat'].to_list()
        daftar_ip_perangkat = perangkat_table['IP Address'].to_list()
        return daftar_nama_perangkat, daftar_ip_perangkat
    
    def preview_upload_file(self, uploader_widget):
        read_upload = txt = StringIO(uploader_widget.getvalue().decode("utf-8")).readlines()
        extractor = Extractor()
        if self.module == 'VBM':
            preview_df = extractor.extract_vbm(read_upload)
        elif self.module == 'SG':
            preview_df = extractor.extract_sg(read_upload)
        preview_df = pd.DataFrame(preview_df)
        return preview_df
    
    

    def upload_to_db(self, preview_df):
        pass

    def render(self):
        st.subheader("Upload File Statistik", anchor=False)
        col1, col2, col3 = st.columns(3)
        nama_perangkat_widget = col1.selectbox("Pilih Perangkat", self.daftar_nama_perangkat)
        ip_selected_widget = col2.text_input("IP Address", value=nama_perangkat_widget, disabled=True)
        tipe_perangkat = col2.text_input("Tipe Perangkat", self.module, disabled=True)

        uploader_widget = st.file_uploader("Pilih File Statistik", type='txt', accept_multiple_files=False)
        if uploader_widget:
            preview_df = self.preview_upload_file(uploader_widget)
            st.write("Preview")
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
            
            submit_btn = st.button("Upload", type='primary')
            # if submit_btn:
            #     upload_data(preview_df)
