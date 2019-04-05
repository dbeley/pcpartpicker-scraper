import os
import time
import logging
import argparse
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
    id_page = 0
    builds = []
    old_links = []

    while True:
        id_page = id_page + 1
        url = f"https://pcpartpicker.com/builds/#page={id_page}"
        logger.debug(f"browser.get({url})")
        browser.get(url)
        while True:
            soup = BeautifulSoup(browser.page_source, 'lxml')
            buildlinks = soup.find_all('a', {'class': 'build-link'})
            if buildlinks != old_links:
                old_links = buildlinks
                break
            logger.warning("Same links extracted twice. Retrying in 1 seconds..")
            time.sleep(4)
            old_links = buildlinks
            soup.decompose()
        # browser.get(url)
        # # time.sleep(1)
        # soup = BeautifulSoup(browser.page_source, 'lxml')
        # buildlinks = soup.find_all('a', {'class': 'build-link'})
        # while buildlinks == old_links:
        #     logger.warning("Same links extracted. Retrying..")
        #     browser.get(url)
        #     buildlinks = soup.find_all('a', {'class': 'build-link'})
        #     time.sleep(1)
        logger.debug(f"buildlinks : {buildlinks}")
        if not buildlinks:
            break
        for buildlink in buildlinks:
            builds.append(str(buildlink['href']))
        # old_links = buildlinks
    builds = [f"https://pcpartpicker.com{x}" for x in builds]
    logger.debug(f"builds : {builds}")

    directory = "Exports"
    if not os.path.exists(directory):
        logger.debug("Creating Exports Folder")
        os.makedirs(directory)

    with open('Exports/list_builds_urls.txt', 'w') as f:
        for build in builds:
            f.write(f"{build}\n")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper pcpartpicker.com (builds_urls)')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
