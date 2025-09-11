import argparse
import json
from bs4 import BeautifulSoup  # type: ignore


class HTMLProcessor():
    def __init__(self, config) -> None:
        self.config = config

        pass

    def get_paragraphs(self, soup, ignore_classes):
        paragraphs = []
        for p in soup.find_all("p"):
            parent_divs = p.find_parents("div")
            skip = False
            for div in parent_divs:
                classes = div.get("class", [])
                if any(ignored_class in c for ignored_class in ignore_classes for c in classes):
                    skip = True
                    break
            if not skip:
                paragraphs.append(p.get_text(strip=True))
        return paragraphs

    def get_output_path(self, output_path_root, source):
        source_root = source[:-4]
        output_path = output_path_root + source_root + "json"
        return output_path

    def get_source_title(self, path):
        index = path.rfind("/")
        return path[index + 1:]

    def write_json(self, output, path):
        with open(path, "w") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)

    def process_html_file(self, path):
        ignore_classes = self.config['classes-ignore']
        with open(path, 'r', encoding='utf-8') as f:
            print(f"PROCESSING {path}")
            html = f.read()
            soup = BeautifulSoup(html, "html.parser")

            # get the output json information
            source = self.get_source_title(path)
            paragraphs = self.get_paragraphs(soup, ignore_classes)
            output = {
                "source": source,
                "paragraphs": paragraphs
            }

            # # write to output
            output_path = self.get_output_path(
                self.config['output_path_root'], source)
            self.write_json(output, output_path)

    def process_files(self):
        for path in self.config['paths']:
            self.process_html_file(path)


if __name__ == "__main__":
    # parse args / get config file
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Path to the config file containing the file paths to process.", required=True)
    args = parser.parse_args()
    config_path = args.config
    config = {}
    with open(config_path, 'r') as file:
        config = json.load(file)

    processor = HTMLProcessor(config)
    processor.process_files()
