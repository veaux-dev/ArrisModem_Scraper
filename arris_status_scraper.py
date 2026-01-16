
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
from pathlib import Path
import pandas as pd
import yaml




def fetch_url(url):
    out = requests.get(url, timeout=5)
    soup = bs(out.text, "html.parser")
    return soup

def parse_html(soup, keywords):
    tables = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tbodies = soup.find_all('tbody')
    for tb in tbodies:
        text = tb.get_text(" ", strip=True)
        if all(k in text for k in keywords):
            rows = tb.find_all('tr')
            headers = [td.get_text(strip=True) or 'Channel' for td in rows[0].find_all('td')]
            data = []
          
            for tr in rows[1:]:
                values = [td.get_text(strip=True) for td in tr.find_all('td')]
                data.append(dict(zip(headers, values)))
            for row in data:
                row['Timestamp_Extraccion'] = timestamp
            tables.append(data)
    return tables

def save_to_csv(file, table, dedup:bool=True):
    df_new=pd.DataFrame(table)
    if Path(file).exists():
        df_old = pd.read_csv(file)
        df_all = pd.concat([df_old,df_new], ignore_index=True)
    else:
        df_all = df_new

    if dedup:
        subset_cols = [c for c in df_all.columns if c != "Timestamp_Extraccion"]
        df_all = df_all.drop_duplicates(subset=subset_cols)

    df_all.to_csv(file,index=False)

if __name__ == "__main__":

    with open("config/config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    STATUS_URL = cfg["STATUS_URL"]
    EVENT_URL = cfg["EVENT_URL"]
    OUTPUT_DIR = cfg["OUTPUT_DIR"]

    while True:
        try:
            status_soup = fetch_url(STATUS_URL)
            events_soup = fetch_url(EVENT_URL)

            out_tables = []
            out_tables.extend(parse_html(status_soup, {'Downstream','DCID'}))
            out_tables.extend(parse_html(status_soup, {'Upstream','UCID'}))
            out_tables.extend(parse_html(events_soup, {'Event ID'}))

            save_to_csv(f'{OUTPUT_DIR}/01_Downstream.csv',out_tables[0],False)
            save_to_csv(f'{OUTPUT_DIR}/02_Upstream.csv',out_tables[1],False)
            save_to_csv(f'{OUTPUT_DIR}/03_DOCSIS.csv',out_tables[2],True)
            save_to_csv(f'{OUTPUT_DIR}/04_MTA.csv',out_tables[3],True)

        except Exception as e:
            print("Error",e)

        with open("config/config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        PULL_INTERVAL = cfg["PULL_INTERVAL"]
        time.sleep(PULL_INTERVAL)

