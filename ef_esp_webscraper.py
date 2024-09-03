import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv 

urls_info = [
    {"url": "https://blog.ethereum.org/2024/08/30/esp-allocation-q224", "year": 2024, "quarter": 'Q2'},  
    {"url": "https://blog.ethereum.org/2024/05/14/esp-allocation-q124", "year": 2024, "quarter": 'Q1'},
    {"url": "https://blog.ethereum.org/2024/02/20/esp-allocation-q423", "year": 2023, "quarter": 'Q4'},
    {"url": "https://blog.ethereum.org/2023/12/19/esp-allocation-q323", "year": 2023, "quarter": 'Q3'},
    {"url": "https://blog.ethereum.org/2023/08/15/allocation-update-q2-23", "year": 2023, "quarter": 'Q2'},
    {"url": "https://blog.ethereum.org/2023/06/15/allocation-update-q1-23", "year": 2023, "quarter": 'Q1'},
    {"url": "https://blog.ethereum.org/2023/02/22/allocation-update-q4-22", "year": 2022, "quarter": 'Q4'},
    {"url": "https://blog.ethereum.org/2022/12/07/esp-allocation-q3-22", "year": 2022, "quarter": 'Q3'},
    {"url": "https://blog.ethereum.org/2022/09/07/esp-q1-q2-allocation-update", "year": 2022, "quarter": 'Q2'},
    {"url": "https://blog.ethereum.org/2022/09/07/esp-q1-q2-allocation-update", "year": 2022, "quarter": 'Q1'},
    {"url": "https://blog.ethereum.org/2022/02/15/esp-q3-q4-allocation-update", "year": 2021, "quarter": 'Q4'},
    {"url": "https://blog.ethereum.org/2022/02/15/esp-q3-q4-allocation-update", "year": 2021, "quarter": 'Q3'},
    {"url": "https://blog.ethereum.org/2021/11/04/esp-allocation-update-q2-2021", "year": 2021, "quarter": 'Q2'},
    {"url": "https://blog.ethereum.org/2021/07/01/esp-allocation-update-q1-2021", "year": 2021, "quarter": 'Q1'},
    {"url": "https://blog.ethereum.org/2021/03/22/esp-allocation-update-q4-2020", "year": 2020, "quarter": 'Q4'},
    {"url": "https://blog.ethereum.org/2020/11/25/esp-q3-updates", "year": 2020, "quarter": 'Q3'},
    {"url": "https://blog.ethereum.org/2020/09/08/esp-q2-updates", "year": 2020, "quarter": 'Q2'},
    {"url": "https://blog.ethereum.org/2020/05/07/ecosystem-support-program-allocation-update-q1", "year": 2020, "quarter": 'Q1'},
]

all_data = []

for info in urls_info:
    url = info['url']
    year = info['year']
    quarter = info['quarter']

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    tables = soup.find_all('table', {'role': 'table', 'class': 'chakra-table css-nz8z8i'})

    # Different tables output depending of the report
    if year == 2021 and quarter == 'Q3' or year == 2022 and quarter == 'Q1':
        table = tables[0]  # Take the first table for Q3 2022
    elif year == 2021 and quarter == 'Q4' or year == 2022 and quarter == 'Q2':
        table = tables[1] 
    else:
        table = tables[0] 

    rows = table.find('tbody', class_='css-i54j9x').find_all('tr')

    spend_tag = soup.find_all('p', class_='chakra-text css-gi02ar')
    spend = ''
    for tag in spend_tag:
        strong_tag = tag.find('strong')
        if strong_tag:
            spend_text = strong_tag.get_text(strip=True)
            spend = spend_text.replace('$', '').replace(',', '')
            break  
    
    # Some spending is not possible to scrap directly
    if year == 2020 and quarter == 'Q1':
        spend = '2564000'
    if year == 2020 and quarter == 'Q2':
        spend = '3884000'
    if year == 2020 and quarter == 'Q3':
        spend = '2400000'
    if year == 2020 and quarter == 'Q4':
        spend = '4091000'
    if year == 2021 and quarter == 'Q2':
        spend = '7794000'

    for row in rows:
        cols = row.find_all('td')

        category = project = recipient = description = contact_data = None

        def process_column(col):
            if col.find('a'):
                links = col.find_all('a')
                formatted_texts = []
                for link in links:
                    href = link.get("href")
                    text = link.get_text(strip=True)
                    formatted_texts.append(f'<a href="{href}" target="_blank">{text}</a>')
                return ', '.join(formatted_texts)
            else:
                return col.get_text(strip=True) if col else ''

        if (year == 2020 and quarter == 'Q1') or (year == 2020 and quarter == 'Q2'):
            category = process_column(cols[0])
            project = process_column(cols[1])
            recipient = ''
            description = process_column(cols[2])
            contact_data = process_column(cols[3])
        elif (year == 2020 and quarter == 'Q4') or (year == 2020 and quarter == 'Q3'):
            category = process_column(cols[0])
            project = process_column(cols[1])
            recipient = ''
            description = process_column(cols[2])
            contact_data = ''
        else:   
            if len(cols) > 0:
                category = process_column(cols[0])
            if len(cols) > 1:
                project = process_column(cols[1])
            if len(cols) > 2:
                recipient = process_column(cols[2])
            if len(cols) > 3:
                description = process_column(cols[3])
            if len(cols) > 4:
                contact_data = process_column(cols[4])
            else:
                contact_data = 'NULL'

        all_data.append([category, project, recipient, description, contact_data, url, year, quarter, spend])

columns = ['Category', 'Project', 'Recipient', 'Description', 'Contact', 'URL', 'Year', 'Quarter', 'Spend']
df = pd.DataFrame(all_data, columns=columns)

def escape_single_quotes(text):
    if isinstance(text, str):
        return text.replace("'", "''")
    return text

columns = ['Category', 'Project', 'Recipient', 'Description', 'Contact', 'URL', 'Year', 'Quarter', 'Spend']
df = pd.DataFrame(all_data, columns=columns)

csv_filename = 'output.csv'
df.to_csv(csv_filename, index=False, quoting=csv.QUOTE_ALL)

print(f"Data has been written to {csv_filename}")