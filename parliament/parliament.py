'''
	Justin Chen
	5.20.17
    main.py

    Script for scraping the Commons and Lords Hansard, the Official Report of debates in Parliament website

	Boston University
	Hariri Institute for Computing and Computational Science & Engineering
'''

from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.error import HTTPError
from multiprocessing import Pool
import argparse
import json
import os

num2month = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct',
             11: 'nov', 12: 'dec'}


def daterange(start_date, end_date):
    start = datetime(start_date['year'], start_date['month'], start_date['day'])
    end = datetime(end_date['year'], end_date['month'], end_date['day'])
    curr = start
    while curr <= end:
        yield curr.isoformat(' ').split(' ')[0]
        curr += timedelta(days=1)


def get_sittings(save_dir, base_url, start_date, end_date):
    pool = Pool()

    url_list = []
    for date_args in daterange(start_date, end_date):
        date_url, doc_date = format_url_date(base_url, date_args)
        url_list.append((save_dir, base_url, date_url, doc_date))

    pool.starmap(scrape_thread, url_list)
    pool.close()
    pool.join()


def scrape_thread(save_dir, base_url, date_url, doc_date):
    soup = scrape(date_url)

    if soup != None:
        for x in soup.find_all('span', class_='major-section'):
            if u'xoxo' in x.parent.parent.parent['class']:
                sitting_atag = [d for d in x.children]
                # get the href and text in the html a-tag and store in tuple
                sitting_url = base_url + (sitting_atag[0].get('href'))
                sitting_soup = scrape(sitting_url)

                # get actual text content of sitting
                sitting_content = []
                for s in sitting_soup.find_all('div', class_='house-of-commons-sitting'):
                    sitting_content.append(s.get_text().strip())
                sitting = {'date': doc_date, 'url': sitting_url, 'content': ''.join(sitting_content),
                           'title': sitting_atag[0].text.split('.')[0].lower(), 'author': 'UK Parliament'}
                save_doc(save_dir, sitting, sitting['date'] + '-' + sitting['title'])


def scrape(url):
    try:
        return bs(urlopen(url), 'html.parser')
    except HTTPError:
        # If page does not exist, skip over it
        return None


def format_url_date(base_url, date_obj):
    url_date = date_obj.split('-')
    url_date[1] = num2month[int(url_date[1])]
    doc_date = '-'.join(url_date)
    url_date.insert(0, 'sittings')
    url_date.insert(0, base_url)
    return '/'.join(url_date), doc_date


def save_doc(save_dir, data, filename):
    with open(os.path.join(save_dir, filename + '.json'), 'w', encoding='utf-8') as doc:
        json.dump(data, doc)


def main():
    base_url = 'http://hansard.millbanksystems.com'
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save/',
                        help='Specify name of save directory. If it does not exist, it will be created.')
    parser.add_argument('--start_year', type=int, default=1802, help='Year to start searching from.')
    parser.add_argument('--start_month', type=int, default=7, help='Month to start searching from.')
    parser.add_argument('--start_day', type=int, default=2, help='Day to start searching from.')
    parser.add_argument('--end_year', type=int, default=2006, help='Year to stop searching.')
    parser.add_argument('--end_month', type=int, default=4, help='Month to stop searching inclusive.')
    parser.add_argument('--end_day', type=int, default=24, help='Day to stop searching.')
    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    start_date = {'year': args.start_year, 'month': args.start_month, 'day': args.start_day}
    end_date = {'year': args.end_year, 'month': args.end_month, 'day': args.end_day}

    get_sittings(args.save_dir, base_url, start_date, end_date)

if __name__ == "__main__":
    main()
