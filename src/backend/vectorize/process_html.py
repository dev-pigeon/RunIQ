import argparse
import json
from bs4 import BeautifulSoup  # type: ignore

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--config", help="Path to the config file containing the file paths to process.", required=True)

args = parser.parse_args()
config_path = args.config
config = {}


def get_paragraphs(soup, ignore_classes):
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


with open(config_path, 'r') as file:
    config = json.load(file)


def get_output_path(output_path_root, source):
    source_root = source[:-4]
    output_path = output_path_root + source_root + "json"
    return output_path


def get_source_title(path):
    index = path.rfind("/")
    return path[index + 1:]


def write_json(output, path):
    with open(path, "w") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)


ignore_classes = config['classes-ignore']
for path in config['paths']:
    with open(path, 'r', encoding='utf-8') as f:
        print(f"PARSING {path}")
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")

        # get the output json information
        source = get_source_title(path)
        print(source)
        paragraphs = get_paragraphs(soup, ignore_classes)
        output = {
            "source": source,
            "paragraphs": paragraphs
        }

        # # write to output
        output_path = get_output_path(config['output_path_root'], source)
        write_json(output, output_path)
