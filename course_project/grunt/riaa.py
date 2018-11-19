# Gathering data from RIAA about Gold & Platinum LP/EP/Single and saving into ../data/platinum.csv

# 1. Get list of awards
# 2. Get Award, Artist, Title, Certification date, Label, Format and ID
# 3. Get detailed information by ID: Release date, Category, Type, Certified Units and Genre (from Jan '15)

import re
import ast
import requests
from bs4 import BeautifulSoup


class Row:
    def __init__(self):
        self.award = None
        self.artist = None
        self.title = None
        self.certification_date = None
        self.label = None
        self.format = None
        self.ID = None
        self.release_date = None
        self.category = None
        self.type = None
        self.certified_units = None
        self.genre = None

# ID,Award,Artist,Title,Certification date,Label,Format,Release date,Category,Type,Certified Units,Genre
def save(rows):
    with open('../data/platinum.csv', 'a') as file:
        for row in rows:
            sep = ';'
            file.write(row.ID.replace(sep, '\\' + sep) + sep)
            file.write(row.award.replace(sep, '\\' + sep) + sep)
            file.write(row.artist.replace(sep, '\\' + sep) + sep)
            file.write(row.title.replace(sep, '\\' + sep) + sep)
            file.write(row.certification_date.replace(sep, '\\' + sep) + sep)
            file.write(row.label.replace(sep, '\\' + sep) + sep)
            file.write(row.format.replace(sep, '\\' + sep) + sep)
            file.write(row.release_date.replace(sep, '\\' + sep) + sep)
            file.write(row.category.replace(sep, '\\' + sep) + sep)
            file.write(row.type.replace(sep, '\\' + sep) + sep)
            file.write(row.certified_units.replace(sep, '\\' + sep) + sep)
            file.write(row.genre.replace(sep, '\\' + sep) + '\n')

def parse_list(data):
    parsed_list = []
    for item in data.find_all('tr'):
        parsed_list.append(parse_item(item))
    return parsed_list

js_id_regex = re.compile('(\\d+)')
award_id_regex = re.compile('/icons/(.*)\\.png')
def parse_item(item):
    row = Row()
    row.ID = js_id_regex.search(item.find('a')['onclick']).groups()[0]

    td = item.find_all('td')

    td_award = td[0].find('img')['src']
    award_id = award_id_regex.search(td_award).groups()[0]
    if award_id == '0_big':
        row.award = 'Gold'
    elif award_id == '1_big':
        row.award = 'Platinum'
    else:
        row.award = award_id

    row.artist = td[1].text
    row.title = td[2].text
    row.certification_date = td[3].text
    row.label = td[4].text
    row.format = td[5].text

    return add_details(row)

def add_details(row):
    body = {
        'action': 'load_detail_from_recent',
        'id': row.ID,
        'mobile': 'false'
    }
    response = get_data('https://www.riaa.com/wp-admin/admin-ajax.php', body)
    print('[%d] %s, Get details for %s' % (response.status_code, response.reason, row.ID))

    data_raw = response.text.encode('utf-8').decode('unicode_escape')[1:-1]
    data_raw = data_raw.replace('\\n', '\n').replace('\\/', '/').replace('\\"', '"')
    data_raw = '<table><tbody>' + data_raw + '</tbody></table>'
    data = BeautifulSoup(data_raw, 'html.parser')

    return parse_detailed(row, data)

def parse_detailed(row, data):
    td = data.find('tbody').find('td').find_all('td')

    row.release_date = td[0].text
    row.category = td[2].text
    row.type = td[3].text
    row.certified_units = td[4].text
    row.genre = td[5].text

    return row

def get_data(uri, body):
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://www.riaa.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    return requests.post(uri, data=body, headers=headers)

page_items = 10

for page in range(1, 1000):
    body = {
        'action': 'load_more_result_default',
        'inf': str(page * page_items),
        'sup': str(page_items)
    }
    response = get_data('https://www.riaa.com/wp-admin/admin-ajax.php?ord=desc&col=certification_date', body)
    print('[%d] %s, Page %d' % (response.status_code, response.reason, page))

    data_raw = response.text.encode('utf-8').decode('unicode_escape')[1:-1]
    data_raw = data_raw.replace('\\n', '\n').replace('\\/', '/').replace('\\"', '"')
    data_raw = '<table><tbody>' + data_raw + '</tbody></table>'
    data = BeautifulSoup(data_raw, 'html.parser')

    parsed = parse_list(data)
    save(parsed)
