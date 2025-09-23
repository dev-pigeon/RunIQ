# this class is meant to be used as a utility to process xml sitemaps
# by creating a list of all valid links/html files to download
# this list will then be returned so the downloader.py can loop them and download them to the correct place
# config driven of course


class XMLProcessor:
    def __init__(self, config) -> None:
        self.config = config
        pass

    def process_sitemap(self):
        pass

