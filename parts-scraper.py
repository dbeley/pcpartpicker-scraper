import time
import logging
import argparse
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

logger = logging.getLogger()
temps_debut = time.time()


def get_soup(url):
    return BeautifulSoup(requests.get(url).content, features="lxml")


def main():
    args = parse_args()

    with open(args.file) as f:
        parts_urls = f.read().splitlines()

    dict_parts = {}
    header_found = False
    for index, url in tqdm(
        enumerate(parts_urls), total=len(parts_urls), dynamic_ncols=True
    ):
        dict_part = {}
        logger.debug("url : %s", url)
        while True:
            try:
                soup_url = get_soup(url)
            except Exception as e:
                logger.error(e)
                continue
            break

        dict_part["Category"] = soup_url.find(
            "h3", {"class": "pageTitle--categoryTitle"}
        ).text
        dict_part["Name"] = soup_url.find("h1", {"class": "pageTitle"}).text
        logger.debug(
            "Extracting %s - {dict_part['Category']} - {dict_part['Name']} at {url}",
            index,
        )
        dict_part["Link"] = url
        rating = (
            soup_url.find("section", {"class": "xs-col-11"})
            .text.split("\n")[-3]
            .strip()
        )
        dict_part["Ratings"] = rating.split()[0].replace("(", "")
        dict_part["Average rating"] = rating.split()[-2]

        specs = soup_url.find("div", {"class": "specs"})
        specs_title = [title.text for title in specs.find_all("h3")]
        specs_value = [
            title.next_sibling.next_sibling.text.strip()
            for title in specs.find_all("h3")
        ]
        for t, v in zip(specs_title, specs_value):
            dict_part[str(t)] = str(v)

        # Prices per merchants
        table_merchants = soup_url.find("table", {"class": "xs-col-12"})
        if table_merchants:
            shops = [
                x.find("a")["href"].split("/")[2]
                for x in table_merchants.find_all("td", {"class": "td__logo"})
            ]
            prices = [
                x.text
                for x in table_merchants.find_all(
                    "td", {"class": "td__base priority--2"}
                )
            ]
            for s, p in zip(shops, prices):
                dict_part[f"Price {s}"] = str(p)
        else:
            logger.debug("No prices found.")

        # Reviews
        reviews = soup_url.find_all("div", {"class": "partReviews__review"})
        if reviews:
            list_reviews = []
            for review in reviews:
                id = review.find("div", {"class": "partReviews__name"}).find(
                    "a"
                )["href"]
                rating = len(
                    review.find(
                        "div", {"class": "partReviews__name"}
                    ).find_all("svg", {"class": "shape-star-full"})
                )
                text = review.find(
                    "div", {"class": "partReviews__writeup"}
                ).text
                list_reviews.append({"id": id, "rating": rating, "text": text})
            dict_part["Reviews"] = str(list_reviews)

        soup_url.decompose()

        dict_parts[index] = dict_part

        logger.debug("Exporting partial dict")
        new_dict = {k: [v] for k, v in dict_part.items()}
        df = pd.DataFrame(new_dict)
        with open(f"Exports/pcpartpicker-parts-data.csv", "a") as f:
            if header_found:
                df.to_csv(f, header=False)
            else:
                df.to_csv(f)
                header_found = True
        # if index > 30:
        #     break
        time.sleep(2)

    df = pd.DataFrame.from_dict(dict_parts, orient="index")
    categories = df.Category.unique()
    for category in categories:
        temp_df = df[df["Category"] == category]
        temp_df.dropna(axis=1, how="all", inplace=True)
        filename = f"Exports/pcpartpicker-parts-{category}-data.csv"
        print("Writing %s", filename)
        temp_df.to_csv(filename, sep=";")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper pcpartpicker.com (parts)"
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="File containing the urls",
        default="Exports/list_parts_urls.txt",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
