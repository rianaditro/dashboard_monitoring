import schedule, datetime, sqlite3
import time
import logging

from datetime import timedelta
from scrap import Scraper


# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# get list of ip address
# Membuat atau menghubungkan ke database
conn = sqlite3.connect('main.sqlite')

# Membuat cursor
c = conn.cursor()

all_ip = c.execute('SELECT ip_address, tipe_perangkat FROM perangkat_table').fetchall()

def info(message):
    logging.info(message)
    print(message)

def get_ip_list(all_ip_list, module):
    ip_list = [i[0] for i in all_ip_list if i[1] == module]
    return ip_list   


def append_history(conn, data):
    s = conn.cursor()
    s.execute(f'''INSERT INTO history_upload (upload_id, upload_datetime, ip_address) VALUES ("{data['upload_id']}", "{data['upload_datetime']}", "{data['upload_ip']}")''')
    conn.commit()
               
def append_table(conn, df, tablename):
    df.to_sql(tablename, conn, if_exists='append', index=False)
    
def upload_data(conn, dataframe, ip_address, module):
    upload_datetime = datetime.datetime.now()
    upload_id = upload_datetime.strftime("%Y%m%d%H")+'_ID'
    upload_ip = ip_address
    dataframe = dataframe.assign(upload_id=upload_id,upload_datetime=upload_datetime,upload_ip=upload_ip)
    
    # re-order columns
    if module == 'module_4':
        dataframe = dataframe[['upload_id','upload_datetime','upload_ip','module', '-', 'reset', 'minutes', 'hms', 'calls', 'reject', 'failed', 'coffs', 'smses','asr']]
    elif module == 'module_32':
        dataframe = dataframe[['upload_id','upload_datetime','upload_ip','module', 'sim', 'net', 'minutes', 'hms', 'calls', 'reject', 'failed', 'coffs', 'smses','asr']]
    elif module == 'module_ge':
        dataframe = dataframe[['upload_id','upload_datetime','upload_ip','mobile_port', 'port_status', 'signal_strength', 'call_duration', 'dialed_calls', 'successfull_calls', 'asr', 'acd', 'allocated_ammount', 'consumed_amount']]
    
    # add history data into database
    history_data = {'upload_id':upload_id, 'upload_datetime':upload_datetime, 'upload_ip':upload_ip}
    append_history(conn, history_data)
    # append to database
    append_table(conn, dataframe, f'{module}_table')


vbm_ip_list = get_ip_list(all_ip, 'Perangkat 4 Modul')
ge_ip_list = get_ip_list(all_ip, 'Perangkat GE')
se_ip_list = get_ip_list(all_ip, 'Perangkat 32 Modul')

def scrap_list(scraper, ip_list, module):
    info(f"Scraping {len(ip_list)} of IP Address from {module}")
    for ip in ip_list:
        try:
            df = scraper.get_data(ip, module)
            upload_data(conn, df, ip, module)
            info("Data uploaded to database")
        except Exception as e:
            info(f"Failed to upload data to database: {e}")
            logging.warning(f"Failed to scrape {ip}")

def scrap_job():
    scraper = Scraper()
    info("===================== Updating Data =====================")
    scrap_list(scraper, vbm_ip_list, 'module_4')
    scrap_list(scraper, se_ip_list, 'module_32')
    scrap_list(scraper, ge_ip_list, 'module_ge')
    info("===================== Data Updated =====================")
    del scraper

def daily_delete():
    limit = datetime.datetime.now() - timedelta(hours=6)
    c.execute(f'DELETE FROM history_upload WHERE upload_datetime < "{limit}"')
    c.execute(f'DELETE FROM module_ge_table WHERE upload_datetime < "{limit}"')
    c.execute(f'DELETE FROM module_32_table WHERE upload_datetime < "{limit}"')
    c.execute(f'DELETE FROM module_4_table WHERE upload_datetime < "{limit}"')
    conn.commit()

# Schedule the jobs
schedule.every(2).hours.at("59:59").do(scrap_job)
schedule.every(2).hours.at("50:00").do(daily_delete)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    info("Auto-update data started")
    daily_delete()
    scrap_job()
    try:
        print("Program is running, please let this window open")
        run_scheduler()
    except Exception as e:
        print(e)
        info("Auto-update data stopped")
