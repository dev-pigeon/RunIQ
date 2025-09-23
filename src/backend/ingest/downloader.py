import logging
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename="ingest/ingestion.log",
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class Downloader:
    def __init__(self, storage_directory) -> None:
        self.storage_directory = storage_directory

    def download_links(self, links):
        pass

    def download_link(self, link):
        pass

    def get_file_name(self, link):
        index = link.rfind("/", 0, len(link) - 1)
        if index == -1:
            logger.warning(f"Cannot derive file name from link {link}")
        file_name = link[index:len(link)-1]
        return file_name

    def write_file(self, file_name, html_content):
        pass
