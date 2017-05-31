'''
	Justin Chen
	5.20.17
    main.py

    Script for scraping the Commons and Lords Hansard, the Official Report of debates in Parliament website

    Note: Must be run with Python3 to avoid character encoding issues.

	Boston University
	Hariri Institute for Computing and Computational Science & Engineering
'''
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from multiprocessing import Pool
import argparse
import json
import os
import time
import random
import codecs

reader = codecs.getreader("utf-8")

num2month = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct',
             11: 'nov', 12: 'dec'}

# main paths which containg sitting data
sitemap = [{'sittings': {'sitting_path': 'commons', 'content_class': 'house-of-commons-sitting'}},
           {'lords': {'sitting_path': 'lords', 'content_class': 'house-of-lords-sitting'}},
           {'commons': {'sitting_path': 'commons', 'content_class': 'house-of-commons-sitting'}},
           {'westminster_hall': {'sitting_path': 'westminster_hall', 'content_class': 'westminster-hall-sitting'}},
           {'written_answers': {'sitting_path': 'written_answers', 'content_class': 'commons-written-answers-sitting'}},
           {'written_statements': {'sitting_path': 'written_statements',
                                   'content_class': 'commons-written-statements-sitting'}},
           {'lords_reports': {'sitting_path': 'lords_reports', 'content_class': 'house-of-lords-report'}},
           {'grand_committee_report': {'sitting_path': 'grand_committee_report',
                                       'content_class': 'grand-committee-report-sitting'}}]


def daterange(start_date, end_date):
    start = datetime(start_date['year'], start_date['month'], start_date['day'])
    end = datetime(end_date['year'], end_date['month'], end_date['day'])
    curr = start
    while curr <= end:
        yield curr.isoformat(' ').split(' ')[0]
        curr += timedelta(days=1)


def get_sittings(save_dir, base_url, start_date, end_date, parallel):
    url_list = []
    for date_args in daterange(start_date, end_date):
        for site_path in sitemap:
            date_url, doc_date = format_url(base_url, site_path, date_str=date_args)
            if parallel:
                url_list.append((save_dir, base_url, date_url, doc_date))
            else:
                scrape_thread(save_dir, base_url, date_url, doc_date)

    if parallel:
        pool = Pool()
        pool.starmap(scrape_thread, url_list)
        pool.close()
        pool.join()


def scrape_thread(save_dir, base_url, date_url, doc_date):
    # Random delay to space out requests to mitigate overwheeling the server
    time.sleep(random.uniform(0, 10))

    # Need to correctly pair the URLs and titles from the titles in the API
    bs_page = scrape(date_url[:-3])

    # Get a-tag text and href
    try:
        atags = [(tag.string.strip(), tag['href']) for tag in bs_page.findAll('a', href=True)]
    except AttributeError:
        # Occurs when the page does not exist. Page may not exist because URLs were generated brute force.
        return

    page_text = scrape_text(bs_page)
    # Items listed on this page are either links to sittings or titles to pages with sittings
    # Items directly to sittings are listed as e.g. "Preamble 8 words", so need to separate these 2 types of items
    line_indices = [page_text.index(c) - 1 for c in page_text if 'words' in c]
    titles = [page_text[t].strip() for t in line_indices]

    sittings = [tag for tag in atags for t in titles if t in tag]

    for sit in sittings:
        sitting_url = ''.join([base_url, sit[1]])
        sitting_soup = scrape(sitting_url)
        visible_text = ''.join(sitting_soup.findAll(text=True))

        # Find second occurrence of title and discard all text before it
        # Assuming that the title occurs only twice on each sitting page, once at the top
        #   and again before the actual sitting text - basing this on the few pages I've seen so far
        discard_from = visible_text.find(sit[0]) + len(sit[0])
        visible_text = visible_text[discard_from:]
        start_pos = visible_text.find(sit[0])

        # Find end of sitting text and ignore misc. text from page
        end_pos_back = visible_text.find('Back to')
        end_pos_forw = visible_text.find('Forward to')

        if end_pos_back == -1 and end_pos_forw == -1:
            end_pos = len(visible_text)
        elif end_pos_back != -1:
            end_pos = end_pos_back
        else:
            end_pos = end_pos_forw

        sitting_text = visible_text[start_pos:end_pos]
        text_split = [x.strip() for x in sitting_text.split('§')]
        header = [x for x in text_split[0].split('\n') if len(x) > 0][:-1]

        # header[0] - sitting title, header[1] - data and volume, text_split[i] - i-th paragraph/speech
        content = {'header': header, 'text': text_split[1:]}

        sitting = {'date': doc_date[:-3], 'url': sitting_url, 'content': content, 'author': 'UK Parliament'}
        save_doc(save_dir, sitting, sitting['date'] + '-' + header[0][:-1].lower().replace(' ', '_'))


# Handles scraping API calls and raw HTML
def scrape(url):
    try:
        if url.endswith('.js'):
            return json.load(reader(urlopen(url)))
        else:
            return bs(urlopen(url).read(), 'html.parser')
    except HTTPError:
        # If page does not exist, skip over it
        return None
    except (TimeoutError, URLError) as e:
        if e.reason == 'no host given':
            return None
        time.sleep(random.uniform(1.5, 5))
        return scrape(url)


def scrape_text(bs_html):
    return list(filter(lambda x: x != '\n', bs_html.findAll(text=True)))


def format_url(base_url, site_path, date_str=''):
    if len(date_str) > 0:
        url_date = date_str.split('-')
        url_date[1] = num2month[int(url_date[1])]
        url_date[2] = url_date[2] + '.js'
        doc_date = '-'.join(url_date)
        key = [k for k in site_path][0]
        url_date.insert(0, key)
        url_date.insert(0, base_url)
        return '/'.join(url_date), doc_date
    else:
        return ''.join([base_url, site_path])


def save_doc(save_dir, data, filename):
    if len(filename) > 50:
        filename = '_'.join(filename[:50].strip().split())

    with open(os.path.join(save_dir, filename + '.json'), 'w', encoding='utf-8') as doc:
        json.dump(data, doc)


def resume_date(save_dir):
    files = os.listdir(save_dir)
    files.sort()
    return files[len(files) - 1].split('-')[:3]


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
    parser.add_argument('--resume', type=bool, default=False,
                        help='Resume searching from last date and do not set the start and end date range.')
    parser.add_argument('--parallel', type=bool, default=False, help='Parallelize scraping.')
    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    if args.resume:
        last = resume_date(args.save_dir)
        last[1] = (list(num2month.keys())[list(num2month.values()).index(last[1])])

        start_date = {'year': int(last[0]), 'month': int(last[1]), 'day': int(last[2])}
    else:
        start_date = {'year': args.start_year, 'month': args.start_month, 'day': args.start_day}

    end_date = {'year': args.end_year, 'month': args.end_month, 'day': args.end_day}

    get_sittings(args.save_dir, base_url, start_date, end_date, args.parallel)


if __name__ == "__main__":
    main()
