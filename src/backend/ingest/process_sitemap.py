# this class is meant to be used as a utility to process xml sitemaps
# by creating a list of all valid links/html files to download
# this list will then be returned so the downloader.py can loop them and download them to the correct place
# config driven of course
import argparse
import json
from bs4 import BeautifulSoup  # type: ignore


class XMLProcessor:
    def __init__(self, config) -> None:
        self.config = config
        pass

    def open_xml_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_xml = file.read()
        return raw_xml

    def process_sitemap(self):
        xml_file = self.open_xml_file(self.config['sitemap_path'])
        download_links = self.get_download_links(xml_file)
        return download_links

    def get_download_links(self, xml_file):
        soup = BeautifulSoup(xml_file, 'xml')
        link_tags = soup.find_all('loc')
        all_links = [tag.text for tag in link_tags]
        valid_links = self.filter_links(all_links)
        return valid_links

    def filter_links(self, all_links):
        key = self.config['search_key']
        training_links = [link for link in all_links if key in link]
        ignored_domains = self.config['ignored_domains']
        valid_training_links = [link for link in training_links if not any(
            ignored_domain in link for ignored_domain in ignored_domains)]
        return valid_training_links


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
