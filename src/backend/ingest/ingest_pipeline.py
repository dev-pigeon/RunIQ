import argparse
import json
from ingest.process_sitemap import XMLProcessor
from ingest.downloader import Downloader


def run(config):
    for ingestion_group in config['ingestion_groups']:
        processor = XMLProcessor(ingestion_group['sitemap_config'])
        downloader = Downloader(ingestion_group['downloader_config'])
        download_links = processor.process_sitemap()
        links = download_links[:5]
        downloader.download_links(links)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config-path", help="Path to config file for ingestion pipeline.", required=True)
    args = parser.parse_args()
    config_path = args.config_path

    with open(config_path, 'r') as file:
        config = json.load(file)

    run(config)
