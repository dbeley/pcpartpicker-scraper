import time
import logging
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger()
temps_debut = time.time()


def get_soup(url):
    return BeautifulSoup(requests.get(url).content, features='lxml')


def main():
    args = parse_args()
    file = args.file

    with open(file) as f:
        parts_urls = f.read().splitlines()

    dict_parts = {}
    for index, url in enumerate(parts_urls):
        dict_part = {}
        soup_url = get_soup(url)
        dict_part['Category'] = soup_url.find('h4', {'class': 'kind'}).text
        dict_part['Name'] = soup_url.find('h1', {'class': 'name'}).text
        print(f"Extracting {index} - {dict_part['Category']} - {dict_part['Name']} at {url}")
        dict_part['Link'] = url
        dict_part['Average rating'] = soup_url.find('span', {'itemprop': 'ratingValue'}).text
        dict_part['Ratings'] = soup_url.find('span', {'itemprop': 'ratingCount'}).text

        specs = soup_url.find('div', {'class': 'specs block'})
        specs_title = []
        specs_value = []
        for title in specs.find_all('h4'):
            specs_title.append(title.text)
            specs_value.append(title.next_sibling.strip())
        for t, v in zip(specs_title, specs_value):
            dict_part[str(t)] = str(v)

        # Reviews
        reviews = soup_url.find_all('div', {'class': 'comment-content'})
        if reviews:
            # logger.debug(f"reviews : {reviews}")
            list_reviews = []
            for review in reviews:
                user = review.find('a', {'class': 'comment-username'}).text
                rating = len(review.find_all('li', {'class': 'full-star'}))
                text = review.find('div', {'class': 'comment-message markdown'}).text
                list_reviews.append({'user': user,
                                     'rating': rating,
                                     'text': text})
            dict_part['Reviews'] = str(list_reviews)

        soup_url.decompose()

        dict_parts[index] = dict_part

    df = pd.DataFrame.from_dict(dict_parts, orient='index')
    categories = df.Category.unique()
    for category in categories:
        temp_df = df[df['Category'] == category]
        filename = f"Exports/pcpartpicker-parts-{category}-data.csv"
        print(f"Writing {filename}")
        temp_df.to_csv(filename, sep=";")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper pcpartpicker.com (parts)')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-f', '--file', type=str, help='File containing the urls', default="Exports/list_parts_urls.txt")
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
