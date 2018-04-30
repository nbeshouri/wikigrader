"""
This module contains the scraper functions needed to scrape raw
data from Wikipedia.

"""

import requests
from bs4 import BeautifulSoup
import re
import random
import time
import joblib
import numpy as np
import traceback
import os
import glob
import itertools


table_labels = [
    'ID',
    'Wikidata ID',
    'Page size',
    'Total edits',
    'Editors',
    'Assessment',
    'Bugs',
    'Page watchers',
    'Pageviews (60 days)',
    'IP edits',
    'Bot edits',
    '(Semi-)automated edits',
    'Reverted edits',
    'First edit',
    'Latest edit',
    'Max. text added',
    'Max. text deleted',

    'Average time between edits (days)',
    'Average edits per user',
    'Average edits per day',
    'Average edits per month',
    'Average edits per year',
    'Edits in the past 24 hours',
    'Edits in the past 7 days',
    'Edits in the past 30 days',
    'Edits in the past 365 days',
    'Edits made by the top 10% of editors',

    'Links to this page',
    'Redirects',
    'Links from this page',
    'External links',
    'Categories',
    'Files',
    'Templates',

    'Characters',
    'Words',
    'Sections',
    'References',
    'Unique references'
]


figure_labels = [
    'Accounts',
    'IPs',
    'Major edits',
    'Minor edits',
    'Top 10%',
    'Bottom 90%'
] 


data_dir_path = os.path.join(os.path.dirname(__file__), 'data')
scrape_data_file_path = os.path.join(data_dir_path, 'raw_scrape_data.pickle')


def _extract_fig_val(label, soup):
    """Extract the string value of the figure legend field given label."""
    label_tag = soup.find('span', class_='legend-label', string=label)
    value_tag = label_tag.find_next_sibling('span', class_='legend-value')
    return value_tag.string.strip().split()[1]


def _extract_table_val(label, soup):
    """Extract the string value of the table field with given label."""
    
    def table_label_filter(node):
        """Return true if node is td node with the requested label."""
        if node.name == 'td':
            # Check for the simple case where the label is the string
            # value of the td node.
            if node.string == label:
                return True
            # Handle the case where the label is part of a
            # link that that's the child of the td node.
            for child in node.children:
                if (child.string is not None
                        and child.string.strip() == label):
                    return True
        return False
    
    label_td_tag = soup.find(table_label_filter)
    # Not all article stats pages have all fields.
    if label_td_tag is None:
        return None
    data_td_tag = label_td_tag.find_next_sibling('td')
    if data_td_tag is None:
        print('data tag is None', label)
    # Use .stripped_strings instead of .string to handle
    # the case where the data string is in a link node
    # that's a childof the td node.
    return list(data_td_tag.stripped_strings)[0].split('\n')[0]


def scrape_article(article_name):
    """Scrape the article and return a dict of field value pairs."""
    url = f'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{article_name}?'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    table_pairs = [(label, _extract_table_val(label, soup)) for label in table_labels]
    fig_pairs = [(label, _extract_fig_val(label, soup)) for label in figure_labels]
    data_dict = dict(table_pairs + fig_pairs)
    data_dict['Name'] = article_name
    return data_dict


def get_article_name(grade):
    """Find a the name of a random article with the given grade."""
    url = f'https://en.wikipedia.org/wiki/Special:RandomInCategory/'
    simple_cases = ('Featured_articles', 'Good_articles')
    complex_cases = ('A', 'B', 'C', 'Start', 'Stub')
    abrev_to_full_name = {'FA': 'Featured_articles', 'GA': 'Good_articles'}

    if grade in abrev_to_full_name:
        grade = abrev_to_full_name[grade]

    # For the simple cases, you can get a random article of given
    # grade just by going to a url.
    if grade in simple_cases:

        url += grade
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        # Get the canonical link and extract the name.
        link_tag = soup.find('link', rel='canonical')
        return re.search(r'https://en.wikipedia.org/wiki/(.*)', link_tag['href']).group(1)

    # In the complex cases it takes you to a random subcategory page, e.g. 
    # "Start-Class Computational Biology articles", which we then
    # need to pick a random sample from. The links are also in 
    # to the "Talk" pages of the article for some reason, but it's
    # still straightforward to extract the name of the article.
    
    # TODO: Some of these pages have more articles then can fit on a page,
    # which I don't handle here. This means that there are some articles that
    # will never be sampled.
    
    elif grade in complex_cases:

        url += f'{grade}-Class_articles'
        # Have to use a while loop here because some of these categories
        # are empty.
        while True:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            a_tags = soup.find_all('a', href=re.compile(r"/wiki/Talk:"))
            if a_tags:
                a_tag = random.choice(a_tags)
                return re.search(r':(.*)', a_tag['href']).group(1)
            time.sleep(0.1)

    raise ValueError("The requested article grade isn't recongnized")


def scrape_articles(article_count, log_freq=100, save=True):
    """
    Scrape article data and optionally store the results.
    
    The scapper cycles through each class of articles, finds
    the name of a random article in that class, and then attempts
    to scrape that article. It does not check for duplicates, so
    the total number of unique articles scraped in each class will
    vary.
    
    A `KeyboardInterrupt` will abort scraping wihtout destroying the
    data scraped so far.
    
    Args:
        article_count (int): The total number of articles to scrape.
        log_freq (int): How often to print a status message.
        save (bool): Whether or not to try to save the article data.
            New data will be concatenated to old data. Defaults to `True`.
    
    """
    article_data = []
    grades = ['FA', 'A', 'GA', 'B', 'C', 'Start', 'Stub']
    grade_cyler = itertools.cycle(grades)
    
    try:
        
        while len(article_data) < article_count:
            grade = next(grade_cyler)
            article_to_scrap = get_article_name(grade)
            # Using a try block to prevent premature abort
            # in case page has unexpected structure.
            try:
                data = scrape_article(article_to_scrap)
                article_data.append(data)
            except Exception as e:
                print(f'Failed to scrape article "{article_to_scrap}".')
                traceback.print_exc()
            if len(article_data) % log_freq == 0:
                print(f'Scrapped {len(article_data)} so far. Last scraped "{article_to_scrap}".')
            # Wait a momment to prevent getting banned.
            delay = 0.1 + np.abs(np.random.normal(0, 1.1))
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print(f'Aborting the the scrape with {len(article_data)} new articles scraped.')
        
    if save:
        if os.path.isfile(scrape_data_file_path):
            article_data += joblib.load(scrape_data_file_path)    
        joblib.dump(article_data, scrape_data_file_path)
        
    return article_data
