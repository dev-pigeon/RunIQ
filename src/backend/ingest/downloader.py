import logging
import requests  # type: ignore
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename="ingest/ingestion.log",
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class Downloader:
    def __init__(self, storage_directory) -> None:
        self.storage_directory = storage_directory

    def download_links(self, links):
        try:
            for link in links:
                html = self.download_link(link)
                file_path = self.storage_directory + self.get_file_name(link)
                self.write_file(file_path, html)

        except requests.RequestException as e:
            logger.warning(e)
        except ValueError as e:
            logger.warning(e)
        except FileNotFoundError as e:
            logger.error(e)
            sys.exit()

    def download_link(self, link):
        try:
            response = requests.get(link)
            response.raise_for_status()
            html = response.text
            logger.debug(f"Successfully downloaded html file from {link}")
            return html
        except requests.RequestException:
            raise requests.RequestException(
                f"Could not download html file at {link}")

    def get_file_name(self, link):
        index = link.rfind("/", 0, len(link) - 1)
        if index == -1:
            raise ValueError(f"Cannot derive file name from link {link}")
        file_name = link[index:len(link)-1]
        return file_name + ".html"

    def write_file(self, file_path, html_content):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file.write(html_content)
            logger.debug(f"Wrote file to {file_path}")
        except FileNotFoundError:
            raise FileNotFoundError(
                "Storage directory does not exist. Please check the path and try again.")
