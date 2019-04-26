import os
import time
import logging
import argparse
import requests
import itertools
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def main():
    args = parse_args()

    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    url_index = "https://pcpartpicker.com/products"
    soup_index = BeautifulSoup(requests.get(url_index).content, features='lxml')
    # cat_products = soup_index.findAll('div', {'class': 'block'})
    cat_products = [x for y in soup_index.findAll('div', {'class': 'block'}) for x in y.findAll('li') if y.find('li')]
    # cat_products = soup_index.find('div', {'class': 'block'}).find_all('li')
    soup_index.decompose()

    all_products = []
    for cat in cat_products:
        index_page = 0
        while True:
            index_page += 1
            cat_link = f"https://pcpartpicker.com{cat.find('a')['href']}#page={index_page}"
            cat_name = cat.text
            logger.debug(f"Catégorie : {cat}, Page : {index_page}")
            browser.get(cat_link)
            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            products = soup.find_all('td', {'class': 'td__name'})
            soup.decompose()
            if not products:
                logger.debug("No products found")
                break
            products = [f"https://pcpartpicker.com{x.find('a')['href']}" for x in products]
            all_products.append(products)

    all_products = list(itertools.chain.from_iterable(all_products))
    logger.debug(f"products : {all_products}")

    directory = "Exports"
    if not os.path.exists(directory):
        logger.debug("Creating Exports Folder")
        os.makedirs(directory)

    with open('Exports/list_parts_urls.txt', 'w') as f:
        for part in all_products:
            f.write(f"{part}\n")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper pcpartpicker.com (parts-urls)')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
