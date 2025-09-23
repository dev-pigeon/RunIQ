# this class is meant to be used as a utility to process xml sitemaps
# by creating a list of all valid links/html files to download
# this list will then be returned so the downloader.py can loop them and download them to the correct place
# config driven of course
import argparse
import json
from bs4 import BeautifulSoup  # type: ignore
from datetime import datetime, timezone
import logging

logger = logging.getLogger()
logging.basicConfig(filename="ingest/ingestion.log", level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class XMLProcessor:
    def __init__(self, config) -> None:
        self.config = config
        pass

    def open_xml_file(self, file_path):
        logger.debug(f"Opening file found at {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_xml = file.read()
                return raw_xml
        except FileNotFoundError:
            logger.error(f"FILE NOT FOUND {file_path}")

    def process_sitemap(self):
        path = self.config['sitemap_path']
        logger.info(f"Processing site map {path}")
        xml_file = self.open_xml_file(path)
        download_links = self.get_download_links(xml_file)
        logger.info(f"Finished processing sitemap {path}")
        return download_links

    def get_download_links(self, xml_file):
        soup = BeautifulSoup(xml_file, 'xml')
        all_urls = soup.find_all('url')
        valid_links = self.filter_urls(all_urls)
        return valid_links

    def filter_urls(self, all_urls):
        filtered_links = []
        for url in all_urls:
            link = url.find("loc").text
            last_mod = url.find("lastmod").text
            if self.url_is_valid(link, last_mod):
                logger.debug(f"Adding link {link}")
                filtered_links.append(link)
        return filtered_links

    def url_is_valid(self, link, last_mod):
        # valid if does not contain the thing and if last mod is within cuttoff years
        return self.link_not_expired(last_mod) and self.link_is_valid(link)

    def link_not_expired(self, last_mod):
        now = datetime.now(timezone.utc).year
        last_mod_date = datetime.fromisoformat(last_mod).year
        document_age = now - last_mod_date
        return document_age <= self.config['max_age_years']

    def link_is_valid(self, link):
        key = self.config['search_key']
        ignored_domains = self.config['ignored_domains']
        return key in link and not any(ignored_domain in link for ignored_domain in ignored_domains)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config-path", help="Path to config file for XMLProcessor.", required=True)
    args = parser.parse_args()
    config_path = args.config_path

    with open(config_path, 'r') as file:
        config = json.load(file)

    processor = XMLProcessor(config)
    download_links = processor.process_sitemap()
