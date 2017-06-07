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
from urllib.error import HTTPError, URLError
from multiprocessing import Pool, Process
import argparse
import json
import os
import time
import random
import codecs
import pickle
import re
import logging

reader = codecs.getreader("utf-8")

base_url = 'http://hansard.millbanksystems.com'

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


def get_sittings(save_dir, start_date, end_date, parallel):
    timeline=[]
    chkpt_dir = os.path.join(save_dir, 'chkpt/timeline_urls.p')
   
    if not os.path.exists(chkpt_dir):
        # brute force generate all possible URLs in the date range. Some may not exists.
        for date_args in daterange(start_date, end_date):
            for site_path in sitemap:
                date_url, doc_date = format_url(site_path, date_str=date_args)
                timeline.append((save_dir, date_url, doc_date))

        save(chkpt_dir, timeline)
    else: 
        timeline = find_range(start_date, end_date, load_pickle(chkpt_dir))


    if parallel:
        pool = Pool()
        pool.starmap(scrape_thread, timeline)
        pool.close()
        pool.join()
    else:
        for url in timeline:
            scrape_thread(url[0], url[1], url[2])


def json2str_date(s):
    return '-'.join([str(s['year']), '%02d'%s['month'], '%02d'%s['day']])


def find_range(start, end, timeline):
    if type(start) != type(end):
        raise Exception('find_range(start, end, timeline): Both inputs start and end must be of the same type (dict, str).')

    if not isinstance(start, str) and not isinstance(start, dict):
        raise Exception('find_range(): Unsupported type. ', str(type(start)),' Must be type str or dict.')

    if isinstance(start, dict):
        start = json2str_date(start)
        end = json2str_date(end)

    start = ''.join([start, '.js'])
    end = ''.join([end, '.js'])

    if start == '1802-07-02.js' and end == '2006-04-24.js':
        return timeline

    s = e = 0

    for i, t in enumerate(timeline):
        # find the start date
        if t[3] == start:
            s = i

        # find the end date
        if t[3] == end:
            e = i
            break

    return timeline[s:e]


def scrape_thread(save_dir, date_url, doc_date):

    # Need to correctly pair the URLs and titles from the titles in the API
    bs_page = scrape(date_url[:-3])

    if bs_page == None:
        return

    # Get a-tag text and href
    try:
        atags = [(tag.string.strip(), tag['href']) for tag in bs_page.findAll('a', href=True)]
    except AttributeError:
        # Occurs when the page does not exist. Page may not exist because URLs were generated brute force.
        # so just skip
        return

    page_text = scrape_text(bs_page)

    # Items listed on this page are either links to sittings or titles to pages with sittings
    # Items directly to sittings are listed as e.g. "Preamble 8 words", so need to separate these 2 types of items
    # Potential problem is "words" appears in the section title and is not a sitting title
    line_indices = [page_text.index(c) - 1 for c in page_text if 'words' in c]
    titles = [page_text[t].strip() for t in line_indices]

    sittings = [tag for tag in atags for t in titles if t in tag]

    if date_url.split('/')[3] == 'sittings':
        # Save API JSON
        api = scrape(date_url)
        save(os.path.join(save_dir, 'api', ''.join([doc_date[:-3], '.js'])), api)

        # Save all valid sitting titles on this date
        sit_dict = {}
        for x, y in sittings:
            sit_dict.setdefault(remove_unicode(x), y)
        title = doc_date[:-3]

        save(os.path.join(save_dir, 'chkpt', 'sittings', ''.join([title, '.js'])), sit_dict)

    for sit in sittings:
        scraped = scrape_sitting(sit)
        if scraped != None:
            sitting_url, content = scraped
            save_doc(save_dir, doc_date, sitting_url, content)


# Input: (title, partial sitting URL)
def scrape_sitting(sit):
    sitting_url = ''.join([base_url, sit[1]])
    # sitting_url = 'http://hansard.millbanksystems.com/lords/1803/dec/14/minutes'
    sitting_soup = scrape(sitting_url)
    visible_text = ''.join(sitting_soup.findAll(text=True))

    # Find second occurrence of title and discard all text before it
    # Assuming that the title occurs only twice on each sitting page, once at the top
    #   and again before the actual sitting text - basing this on the few pages I've seen so far
    discard_from = visible_text.find(sit[0]) + len(sit[0])
    visible_text = visible_text[discard_from:]
    start_pos = visible_text.find(sit[0])

    sitting_text = visible_text[start_pos:]
    split_sym = '§'
    text_split = ''.join([x for x in sitting_text.split(split_sym) if len(x.strip()) > 0]).split('\n')
    text_split = [x.strip() for x in text_split if len(x.strip()) > 0]

    if len(text_split) == 0:
        return None

    # Find end of sitting text and ignore misc. text from page

    end_pos_back = end_pos_forw = end_pos_note = -1
    for i, x in enumerate(text_split):
        if 'Back to' in x:
            end_pos_back = i
        if 'Forward to' in x:
            end_pos_forw = i
        if 'Noticed a typo?' in x:
            end_pos_note = i

    ends = [end_pos_back, end_pos_forw, end_pos_note]

    if sum(ends) > -3:
        end_pos = min([x for x in ends if x != -1])
        text_split = text_split[:end_pos]

    cols = [tag.text.strip() for tag in sitting_soup.findAll('a', href=True) if 'name' in tag.attrs and 'column_' in tag.attrs['name']]

    if len(cols) > 0:
        try:
            delim_header = text_split.index(cols.pop(0))
            header = text_split[:delim_header]
            text_split = [x for x in text_split[delim_header+1:] if x not in cols]
        except ValueError:
            logging.info(text_split)
            header = text_split[:2]
            text_split = text_split[2:]
        
        return sitting_url, {'header': header, 'text': text_split}
    else:
        return sitting_url, {'header': text_split[:2], 'text': text_split[2:]}

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
        time.sleep(random.uniform(1.5, 10))
        return scrape(url)


# Get all visible text on the page
def scrape_text(bs_html):
    return list(filter(lambda x: x != '\n', bs_html.findAll(text=True)))


def format_url(site_path, date_str=''):
    if len(date_str) > 0:
        url_date = date_str.split('-')
        url_date[2] = url_date[2] + '.js'
        doc_date = '-'.join(url_date)
        url_date[1] = num2month[int(url_date[1])]
        key = [k for k in site_path][0]
        url_date.insert(0, key)
        url_date.insert(0, base_url)
        return '/'.join(url_date), doc_date
    else:
        return ''.join([base_url, site_path])


# full path to file including the extension
def load_pickle(filepath):
    with open(filepath, 'rb') as readfile:
        return pickle.load(readfile)


def save(filepath, obj):
    if filepath.endswith('.p'):
        with open(filepath, 'wb') as writefile:
            pickle.dump(obj, writefile)
    elif filepath.endswith('.js'):
        with open(filepath, 'w') as writefile:
            json.dump(obj, writefile)
    else:
        raise Exception('Cannont save. Unfamiliar file extension.')


def save_doc(save_dir, doc_date, sitting_url, content):
    header = content['header']
    sitting = {'date': doc_date[:-3], 'url': sitting_url, 'content': content, 'author': 'UK Parliament'}
    save_dir = os.path.join(save_dir, 'sittings')

    # Sitting name without backslash, periods, single and double quotes
    title = filter_title(header[0])
    if len(title) > 50:
        title = title[:50]

    filename = '.'.join(['-'.join([sitting['date'], sitting_url.split('/')[3], title]), 'js'])

    save(os.path.join(save_dir, filename), sitting)


def remove_unicode(s):
    return ''.join([c for c in s if ord(c) < 128])


def filter_title(t):
    return re.sub('[^0-9a-zA-Z_]+', '', t.replace(' ', '_')).lower()


def recent(a, b):
    if type(a) != type(b):
        raise Exception('recent(a, b): Both inputs a and b must be of the same type.')    
    a_ = a
    b_ = b

    if isinstance(a, dict):
        a = json2str_date(a)
        b = json2str_date(b)
        
    return a_ if datetime.strptime(a, "%Y-%m-%d") > datetime.strptime(b, "%Y-%m-%d") else b_
    

def resume(save_dir, chk_sit_dir, sit_dir):
    # Check all sitting titles in the date range it should have gotten, which will be in chk_sit_dir
    #  against the sittings that were actually obtained in sit_dir
    titles_dict = {}
    sittings = {}
    chk_sit_files = []
    most_recent = '0001-01-01'

    for i, doc_date in enumerate(os.listdir(chk_sit_dir)):
        with open(os.path.join(chk_sit_dir, doc_date)) as datefile:
            
            # JSON key: sitting title, value: partial URL
            date_sitting = json.load(datefile)
            sittings.update(date_sitting)

            # title of each file is <date>.js
            date = doc_date.split('.')[0]

            most_recent = recent(date, most_recent)

            # iterate through the sittings on this date
            for t in date_sitting:
                filtered_title = filter_title(t)

                # format all sitting titles as the sitting filenames in the sitting directory so can compare
                # to see what should have been scraped
                chk_sit_files.append(''.join([date, '-', date_sitting[t].split('/')[1], '-', filtered_title, '.js']))

                # collect the titles
                titles_dict[filtered_title] = t

    # Retrieve any missing sittings
    sit_dir_files = os.listdir(sit_dir)
    diff = list(set(chk_sit_files) - set(sit_dir_files))

    if len(diff) > 0:
        for sit in diff:
            # each sit file is named using the same convention 
            # e.g. 1803-11-23-commons-boston_election_fetitiom.js
            sit = sit[:-3].split('-')
            doc_date = '-'.join([sit[0], sit[1], sit[2]])+'.js'
            original = remove_unicode(titles_dict[sit[-1]])
            title_url_pair = (original, sittings[original])

            scraped = scrape_sitting(title_url_pair)
            if scraped != None:
                sitting_url, content = scraped
                save_doc(save_dir, doc_date, sitting_url, content)

    last = most_recent.split('-')
    return {'year': int(last[0]), 'month': int(last[1]), 'day': int(last[2])}
        

def check_date(start_date, end_date):
    if recent(start_date, end_date) == start_date and end_date != start_date:
        raise Exception('main(): Start date cannot be more recent than end start')


def main():
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
                        help='Resume searching from last date. Do not set the start and end date range if using this option.')
    parser.add_argument('--parallel', type=bool, default=False, help='Parallelize scraping.')
    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    sit_dir = os.path.join(args.save_dir, 'sittings')
    if not os.path.exists(sit_dir):
        os.makedirs(sit_dir)

    api_dir = os.path.join(args.save_dir, 'api')
    if not os.path.exists(api_dir):
        os.makedirs(api_dir)

    chk_dir = os.path.join(args.save_dir, 'chkpt')
    if not os.path.exists(chk_dir):
        os.makedirs(chk_dir)

    chk_sit_dir = os.path.join(args.save_dir, 'chkpt', 'sittings')
    if not os.path.exists(chk_sit_dir):
        os.makedirs(chk_sit_dir)

    # Set up logging
    logging.basicConfig(filename=''.join([args.save_dir, 'parliament', '.log']),level=logging.DEBUG)

    start_date = {'year': args.start_year, 'month': args.start_month, 'day': args.start_day}
    end_date = {'year': args.end_year, 'month': args.end_month, 'day': args.end_day}

    if args.resume:
        resume_start_date = resume(args.save_dir, chk_sit_dir, sit_dir)

        # Takes the most recent start date in the odd case that the user would like to resume, but would like to start
        # at a more recent date, so this should skip over those dates in between and start with the new start date.
        print(type(resume_start_date))
        print(type(start_date))
        return
        start_date = recent(resume_start_date, start_date)

    check_date(start_date, end_date)
    get_sittings(args.save_dir, start_date, end_date, args.parallel)


if __name__ == "__main__":
    main()