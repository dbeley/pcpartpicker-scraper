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

    with open(args.file) as f:
        builds_urls = f.read().splitlines()

    dict_builds = {}
    for index, build_url in enumerate(builds_urls, 1):
        try:
            dict_build = {}
            soup_build = get_soup(build_url)

            # Basic build informations
            dict_build['Name'] = soup_build.find('h1', {'class': 'pageTitle build__name'}).text
            print(f"Extracting build {index} - {dict_build['Name']} at {build_url}")
            dict_build['Build Link'] = build_url
            dict_build['Description'] = soup_build.find('div', {'class': 'markdown'}).text.replace('\n', '')
            dict_build['Votes'] = soup_build.find('a', {'class': 'actionBox actionBox__vote'}).text
            dict_build['Comments number'] = soup_build.find('a', {'class': 'actionBox__comments'}).text
            dict_build['Author'] = soup_build.find('div', {'class': 'user'}).find('a').text
            # logger.debug(dict_build)

            # Build comments
            # comments_text = [x.text.strip() for x in soup_build.find_all('div', {'class': 'comment-message'})]
            # comments_user = [x.text.strip() for x in soup_build.find_all('a', {'class': 'comment-username'})]
            # list_comments = []
            # for u, t in zip(comments_user, comments_text):
            #     list_comments.append({'username': u, 'content': t})
            # dict_build['Comment'] = str(list_comments)

            # Detailed build informations
            details_title = [x.text for x in soup_build.find_all('h4', {'class': 'group__title'})]
            details_value = [x.text for x in soup_build.find_all('div', {'class': 'group__content'})]
            for t, v in zip(details_title, details_value):
                dict_build[t] = str(v)
            logger.debug(dict_build)

            list_url = soup_build.find('span', {'class': 'header-actions'}).find('a')['href']
            list_url = f"https://pcpartpicker.com{list_url}"

            print(f"Extracting build parts from {list_url}")
            # Parts list
            dict_build['Config Link'] = list_url
            soup_list = get_soup(list_url)
            table_components = soup_list.find('table', {'class': 'xs-col-12'}).find_all('tr', {'class': 'tr__product'})
            old_component_type = "TEST"
            count_component_type = 2
            for component in table_components:
                try:
                    component_type = component.find('td', {'class': 'td__component'}).text.strip()
                    if component_type == '':
                        component_type = f"{old_component_type}_{count_component_type}"
                        count_component_type += 1
                    if not component_type.startswith(old_component_type):
                        count_component_type = 2
                        old_component_type = component_type
                except Exception as e:
                    logger.debug("component_type : %s", e)
                    pass
                try:
                    component_name = component.find('td', {'class': 'td__name'}).text.strip()
                except Exception as e:
                    logger.debug("component_name : %s", e)
                    component_name = "NA"
                    pass
                try:
                    component_final_price = component.find('td', {'class': 'td__price'}).text.strip().replace("Price", "")
                except Exception as e:
                    logger.debug("component_final_price : %s", e)
                    component_final_price = "NA"
                    pass
                try:
                    component_shop = component.find('td', {'class': 'td__where'}).find('a')['href'].split('/')[2]
                except Exception as e:
                    logger.debug("component_shop : %s", e)
                    component_shop = "NA"
                    pass
                dict_build[component_type] = component_name
                dict_build[f"{component_type} Price"] = component_final_price
                dict_build[f"{component_type} Shop"] = component_shop

            logger.debug("Final dict_build : %s", dict_build)
            dict_builds[index] = dict_build
        except Exception as e:
            logger.error("Problem extracting product : %s", e)
        # if index > 4:
        #     break
        time.sleep(2)

    df = pd.DataFrame.from_dict(dict_builds, orient='index')
    filename = f"Exports/pcpartpicker-builds-data.csv"
    print("Writing %s", filename)
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
