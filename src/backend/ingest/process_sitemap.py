# this class is meant to be used as a utility to process xml sitemaps
# by creating a list of all valid links/html files to download
# this list will then be returned so the downloader.py can loop them and download them to the correct place
# config driven of course
import argparse
import json


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
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config-path", help="Path to config file for XMLProcessor.", required=True)
    args = parser.parse_args()
    config_path = args.config_path

    with open(config_path, 'r') as file:
        config = json.load(file)

    processor = XMLProcessor(config)
    processor.process_sitemap()
