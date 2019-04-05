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
        builds_urls = f.read().splitlines()

    dict_builds = {}
    for index, build_url in enumerate(builds_urls):
        try:
            dict_build = {}
            soup_build = get_soup(build_url)

            # Basic build informations
            dict_build['Name'] = str(soup_build.find('h1', {'class': 'name'}).text)
            print(f"Extracting build {index} - {dict_build['Name']} at {build_url}")
            dict_build['Build Link'] = build_url
            dict_build['Description'] = str(soup_build.find('div', {'class': 'markdown'}).text)
            dict_build['Votes'] = str(soup_build.find('div', {'class': 'vote-count'}).text)
            dict_build['Comments number'] = str(soup_build.find('td', {'class': 'action-box-comments'}).text.strip())
            dict_build['Author'] = str(soup_build.find('p', {'class': 'owner'}).find('a').text)

            # Build comments
            comments_text = [x.text.strip() for x in soup_build.find_all('div', {'class': 'comment-message'})]
            comments_user = [x.text.strip() for x in soup_build.find_all('a', {'class': 'comment-username'})]
            list_comments = []
            for u, t in zip(comments_user, comments_text):
                list_comments.append({'username': u, 'content': t})
            dict_build['Comment'] = str(list_comments)

            # Detailed build informations
            details_title = [x.text for x in soup_build.find('div', {'class': 'part-details'}).find_all('h4')]
            details_value = [x.strip() for x in soup_build.find('div', {'class': 'part-details'}) if "\n " in x]
            for t, v in zip(details_title, details_value):
                dict_build[t] = str(v)

            list_url = soup_build.find('span', {'class': 'header-actions'}).find('a')['href']
            list_url = f"https://pcpartpicker.com{list_url}"

            print(f"Extracting build parts from {list_url}")
            # Parts list
            dict_build['Config Link'] = list_url
            soup_list = get_soup(list_url)
            table_components = soup_list.find('table', {'class': 'manual-zebra'}).find_all('tr')
            old_component_type = "TEST"
            count_component_type = 2
            for component in table_components[1:]:
                attr = component.find_all('td')
                try:
                    component_type = attr[0].text.strip()
                    if component_type == '':
                        component_type = f"{old_component_type}_{count_component_type}"
                        count_component_type += 1
                    if not component_type.startswith(old_component_type):
                        count_component_type = 2
                        old_component_type = component_type
                except Exception as e:
                    logger.warning(f"component_type : {str(e)}")
                    pass
                try:
                    component_name = attr[2].text.strip()
                except Exception as e:
                    logger.warning(f"component_name : {str(e)}")
                    pass
                try:
                    component_price = attr[3].text
                except Exception as e:
                    logger.warning(f"component_price : {str(e)}")
                    pass
                try:
                    component_final_price = attr[7].text
                except Exception as e:
                    logger.warning(f"component_final_price : {str(e)}")
                    pass
                try:
                    component_shop = attr[8].text.strip()
                except Exception as e:
                    logger.warning(f"component_shop : {str(e)}")
                    pass
                dict_build[component_type] = component_name
                dict_build[f"{component_type} Price"] = component_price
                dict_build[f"{component_type} Final Price"] = component_final_price
                dict_build[f"{component_type} Shop"] = component_shop

            logger.debug(f"Final dict_build : {dict_build}")
            dict_builds[index] = dict_build
        except Exception as e:
            logger.error(f"Problem extracting product : {str(e)}")

    df = pd.DataFrame.from_dict(dict_builds, orient='index')
    filename = f"Exports/pcpartpicker-builds-data.csv"
    print(f"Writing {filename}")
    df.to_csv(filename, sep=";")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper pcpartpicker.com (builds)')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-f', '--file', type=str, help='File containing the urls', default="Exports/list_builds_urls.txt")
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
