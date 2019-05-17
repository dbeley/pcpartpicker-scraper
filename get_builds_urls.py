import time
import logging
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
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
        logger.debug("browser.get(%s)", url)
        browser.get(url)
        number_of_tries = 0
        while True:
            number_of_tries += 1
            time.sleep(4)
            if number_of_tries > 10:
                logger.warning("More than 10 tries. Waiting 30 seconds...")
                browser.get(url)
                time.sleep(30)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            buildlinks = soup.find_all('a', {'class': 'logGroup__target'})

            if not buildlinks:
                logger.debug("No links found. Exiting")
                break
            if buildlinks != old_links:
                logger.debug("Different links than before. Going to the next page")
                old_links = buildlinks
                break
            logger.warning("Same links extracted twice. Retrying in 4 seconds..")
            old_links = buildlinks
            soup.decompose()

        logger.debug("buildlinks : %s", buildlinks)
        if not buildlinks:
            break
        for buildlink in buildlinks:
            builds.append(str(buildlink['href']))
        # break
    logger.debug("builds : %s", builds)

    directory = "Exports"
    Path(directory).mkdir(parents=True, exist_ok=True)

    with open('Exports/list_builds_urls.txt', 'w') as f:
        for build in builds:
            f.write(f"https://pcpartpicker.com{build}\n")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper pcpartpicker.com (builds_urls)')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
