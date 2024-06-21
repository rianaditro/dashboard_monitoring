import sqlite3
import pandas as pd


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('main.sqlite', check_same_thread=False)
        self.c = self.conn.cursor()
        self.vbm_data = self.get_vbm_data()
        self.sg_data = self.get_sg_data()
        self.ge_data = self.get_ge_data()
        self.home_data = self.get_home_data()
        self.perangkat_table = self.get_perangkat_table()
        self.history_table = self.get_history_upload()

    def data_summary(self, dataframe:pd.DataFrame):
        new_df = pd.DataFrame()
        col_list = ['Upload ID', 'Upload Date', 'Nama Perangkat', 'IP Address', 'Module', 'Mobile Port', 'Call Duration', 'Calls', 'ASR(%)', 'Prev ASR(%)', 'Difference']
        for col in dataframe.columns:
            if col in col_list:
                new_df[col] = dataframe[col]

        new_df = new_df[new_df['ASR(%)'] < self.get_asr_from_db()]
        new_df = new_df[new_df['Calls'] > 0]

        new_df.rename(columns={'Module': 'Mobile Port/Module', 'Mobile Port': 'Mobile Port/Module'}, inplace=True)
        return new_df

    def get_home_data(self):
        vbm_data = self.data_summary(self.get_vbm_data())
        sg_data = self.data_summary(self.get_sg_data())
        ge_data = self.data_summary(self.get_ge_data())
        
        home_data = pd.concat([vbm_data, sg_data, ge_data])
        home_data.sort_values(by='ASR(%)', ascending=True, inplace=True)
        return home_data.reset_index(drop=True)

    def get_data_source(self, module:str):
        if module == 'VBM':
            table_name = 'module_4_table'
            columns = [
            'Upload ID', 'Upload Date', 'IP Address',
            'Module', '-', 'Reset', 'Minutes', 
            'Call Duration', 'Calls', 'Reject', 'Failed', 
            'Coffs', 'Smses','ASR(%)', 'Nama Perangkat'
            ]
        elif module == 'SG':
            table_name = 'module_32_table'
            columns = [
            'Upload ID', 'Upload Date', 'IP Address',
            'Module', 'Sim', 'Net', 'Minutes', 
            'Call Duration', 'Calls', 'Reject', 'Failed', 
            'Coffs', 'Smses','ASR(%)', 'Nama Perangkat'
            ]
        elif module == 'GE':
            table_name = 'module_ge_table'
            columns = [
            'Upload ID', 'Upload Date', 'IP Address', 
            'Mobile Port', 'Port Status', 'Signal Strength',
            'Call Duration', 'Dialed Calls', 'Calls',
            'ASR(%)', 'ACD', 'Allocated', 'Consumed', 'Nama Perangkat'
            ]
        rows = self.c.execute(f"""
                              SELECT 
                                data.*,
                                perangkat.nama_perangkat 
                              FROM 
                                {table_name} AS data 
                              LEFT JOIN 
                                perangkat_table AS perangkat 
                              ON 
                                data.upload_ip = perangkat.ip_address
                              """)
        data_source = pd.DataFrame(rows, columns=columns)

        return data_source
    
    def get_complete_data(self, module:str):
        data_source = self.get_data_source(module)
        # split data by Upload ID reverse to get the latest date as first group
        upload_id_group = [d.reset_index(drop=True) for _, d in data_source.groupby('Upload ID')][::-1]
        # get the latest data only
        complete_data = upload_id_group[0]
        # complete_data = pd.concat(upload_id_group[:-1], axis=0)
        # get the previous ASR data
        prev_df = upload_id_group[1].reset_index(drop=True)
        # prev_df = pd.concat(upload_id_group[1:], axis=0
        #                     ).reset_index(drop=True)
        # add new column
        complete_data['ASR(%)'] = complete_data['ASR(%)'].astype(float)
        complete_data['Prev ASR(%)'] = prev_df['ASR(%)'].astype(float)
        complete_data['Difference'] = complete_data['ASR(%)'] - complete_data['Prev ASR(%)']

        return complete_data
    
    def get_data_display(self, module:str):
        complete_data = self.get_complete_data(module)
        # convert Successfull Calls, Reject, Failed, Coffs, Smses, ASR to float
        for col in complete_data.columns:
            if 'Calls' in col or 'Reject' in col or 'Failed' in col or 'Coffs' in col or 'Smses' in col:
                complete_data[col] = complete_data[col].astype(int)
        # complete_data = complete_data.groupby('Upload ID')
        complete_data = complete_data.sort_values(by=['ASR(%)', 'Upload Date'], ascending=True)
        self.data_display = complete_data.reset_index(drop=True)
        return self.data_display
    
    def get_vbm_data(self):
        data =  self.get_data_display('VBM')
        data = data[[
            'Upload ID', 'Upload Date',
            'Nama Perangkat', 'IP Address', 'Module',
            'Minutes', 'Call Duration', 'Calls', 'Reject', 'Failed',
            'Coffs', 'Smses', 'ASR(%)', 'Prev ASR(%)', 'Difference'
            ]]
        return data
    
    def get_sg_data(self):
        data = self.get_data_display('SG')
        data = data[[
            'Upload ID', 'Upload Date',
            'Nama Perangkat', 'IP Address', 'Module', 'Sim', 'Net',
            'Minutes', 'Call Duration', 'Calls', 'Reject', 'Failed',
            'Coffs', 'Smses', 'ASR(%)', 'Prev ASR(%)', 'Difference'
        ]]
        return data
    
    def get_ge_data(self):
        data = self.get_data_display('GE')
        data = data[['Upload ID', 'Upload Date', 'Nama Perangkat', 'IP Address',
            'Mobile Port', 'Port Status', 'Signal Strength',
            'Allocated', 'Consumed', 'ACD',
            'Call Duration', 'Dialed Calls', 'Calls',
            'ASR(%)', 'Prev ASR(%)', 'Difference']]
        return data

    def get_asr_from_db(self):
        self.c.execute("SELECT asr_value FROM asr_value WHERE id = 1 LIMIT 1")
        rows = self.c.fetchone()[0]
        return rows
    
    def update_asr(self, new_value):
        self.c.execute("UPDATE asr_value SET asr_value = ? WHERE id = 1", (new_value,))
        self.conn.commit()

    def get_history_upload(self):
        latest_upload_id = self.c.execute("""SELECT upload_id FROM history_upload 
                                          ORDER BY upload_datetime DESC LIMIT 1"""
                                          ).fetchall()[0][0]
        history_table = self.c.execute(f"""SELECT p.nama_perangkat, p.ip_address, 
                                       p.tipe_perangkat, MAX(h.upload_datetime) AS last_update, 
                                       CASE 
                                            WHEN MAX(h.upload_datetime) IS NULL THEN 'Never Updated' 
                                            WHEN h.upload_id = '{latest_upload_id}' THEN 'Updated' 
                                            ELSE 'Not Up to Date' 
                                        END AS status 
                                        FROM perangkat_table AS p 
                                        LEFT JOIN history_upload as h 
                                        ON p.ip_address = h.ip_address 
                                        GROUP BY p.ip_address 
                                        ORDER BY last_update ASC"""
                                        ).fetchall()
        
        columns = ['Nama Perangkat', 'IP Address', 'Tipe Perangkat', 'Last Update', 'Status']
        history_table = pd.DataFrame(history_table, columns=columns)

        self.history_table = history_table
        return self.history_table
    
    def filter_tipe_perangkat(self, data:pd.DataFrame, module:str):
        if module == 'VBM':
            data = data[data['Tipe Perangkat'] == 'Perangkat 4 Modul']
        elif module == 'SG':
            data = data[data['Tipe Perangkat'] == 'Perangkat 32 Modul']
        elif module == 'GE':
            data = data[data['Tipe Perangkat'] == 'Perangkat GE']
        else:
            data = data[data['Status'] != 'Updated']
        return data.reset_index(drop=True)
    
    def get_perangkat_table(self):
        rows = self.c.execute(f"SELECT * FROM perangkat_table").fetchall()
        columns = ['Nama Perangkat', 'IP Address', 'Tipe Perangkat']
        perangkat_table = pd.DataFrame(rows, columns=columns)
        return perangkat_table
