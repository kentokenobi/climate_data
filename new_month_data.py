import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

# Separate city and year
def split_city_year(city):
    match = re.match(r'(.+?)（(.+?)）', city)
    if match:
        return match.groups()
    return city, None

df = pd.read_csv('code.csv')

df_base = pd.DataFrame()
year = 2024

for idx, row in df.iterrows():
    name = row.iloc[1]
    code = row.iloc[0]
    label = row.iloc[4].lower()
    lat = row.iloc[7]
    lon = row.iloc[10]
    prefecture = row.iloc[3]

    df_base_point = pd.DataFrame()

    url = f'https://www.data.jma.go.jp/stats/etrn/view/monthly_{label}1.php?prec_no={prefecture}&block_no={code}&year={year}&month=&day=&view='
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Data for that location for that year
    list_max = []
    list_min = []
    list_year = []
    list_month = [month for month in range(1, 13)]
    list_code = []
    lat_list = []
    lon_list = []
    name_list = []

    try:
        table = soup.find('table', class_='data2_s')
        table_tr = table.find_all('tr', class_='mtx')
        for i in table_tr[3:]:
            if label == 's':
                max_temp = i.find_all('td')[8].text
                min_temp = i.find_all('td')[9].text
            else:
                max_temp = i.find_all('td')[6].text
                min_temp = i.find_all('td')[7].text

            list_max.append(max_temp)
            list_min.append(min_temp)
            list_year.append(year)
            list_code.append(code)
            lat_list.append(lat)
            lon_list.append(lon)
            name_list.append(name)

        list_max_r = [item.replace(' )', '') for item in list_max]
        list_min_r = [item.replace(' )', '') for item in list_min]

        df_list = pd.DataFrame(
            zip(name_list, list_code, list_year, list_month, list_max_r, list_min_r, lat_list, lon_list),
            columns=['name', 'code', 'year', 'month', 'max', 'min', 'lat', 'lon']
        )
        df_base_point = pd.concat([df_base_point, df_list], axis=0).replace('///', '')

        time.sleep(0.5)
    except AttributeError:
        pass

    df_base = pd.concat([df_base, df_base_point], axis=0)

df_base.to_csv('new_month_data_add.csv', index=False)
