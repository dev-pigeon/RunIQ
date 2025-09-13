import argparse
import json
from bs4 import BeautifulSoup  # type: ignore


class HTMLProcessor():
    def __init__(self, config) -> None:
        self.config = config

    def get_paragraphs(self, soup, ignore_classes):
        paragraphs = []
        for p in soup.find_all("p"):
            parent_divs = p.find_parents("div")
            skip = False
            for div in parent_divs:
                classes = div.get("class", [])
                if any(ignored_class in c for ignored_class in ignore_classes for c in classes):
                    skip = True

            if not skip:
                paragraphs.append(p.get_text(strip=True))
        return paragraphs

    def get_source_root(self, source):
        return source[:-4]

    def get_output_path(self, source):
        source_root = self.get_source_root(source)
        output_path = self.config['output_path_root'] + source_root + "json"
        print(output_path)
        return output_path

    def get_source_title(self, path):
        index = path.rfind("/")
        return path[index + 1:]

    def write_json(self, output, path):
        with open(path, "w") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)

    def process_tables(self, soup, table_config, source):
        tables = soup.select(table_config['table_selector'])
        results = []
        for table in tables:
            # right here is where I should check for valid table id
            parent_divs = table.find_parents("div")
            skip = False
            invalid_ids = table_config['invalid_table_ids']
            for div in parent_divs:
                table_id = div.get("id", [])
                if any(invalid_id in table_id for invalid_id in invalid_ids):
                    skip = True
                    break

            if not skip:
                table_json = self.process_table(
                    table, table_config, level=source)
                results.append(table_json)

        return results

    def flatten_weeks(self, weeks):
        flat_weeks = []
        for week in weeks:
            flat_week = week['desc']
            for day in week['days']:
                flat_week += day['day'] + ":" + day['workout'] + " \n"
            flat_weeks.append(flat_week)

        return flat_weeks

    def format_level(self, level):
        if "_" in level:
            level = level.replace("_", " ", 1)
        return level

    def process_table(self, table, table_config, level):
        formatted_level = self.format_level(level)
        desc = f"{formatted_level} training plan"
        weeks_data = []

        rows = table.select(table_config['row_selector'])
        for i, row in enumerate(rows):
            week_number = i + 1
            week_title = f"Week {week_number}"
            week_desc = f"{week_title} of training plan for {formatted_level} athlete: \n"

            day_cells = row.select(table_config['day_cells'])
            days = []
            for day_cell, day_header in zip(day_cells, table.select(table_config['day_columns_selector'])):
                day_name = day_header.get_text(strip=True)
                workout = day_cell.get_text(strip=True)
                days.append({"day": day_name, "workout": workout})

            weeks_data.append({
                "week": week_title,
                "days": days,
                "desc": week_desc,
            })

        flat_weeks = self.flatten_weeks(weeks_data)

        table_json = {
            "desc": desc,
            "source_file": level,
            "weeks": flat_weeks
        }

        return table_json

    def process_html_file(self, path):
        ignore_classes = self.config['classes-ignore']
        with open(path, 'r', encoding='utf-8') as f:
            print(f"PROCESSING {path}")
            html = f.read()
            soup = BeautifulSoup(html, "html.parser")

            # get the output json information
            source = self.get_source_title(path)
            paragraphs = self.get_paragraphs(soup, ignore_classes)
            table_jsons = None
            # get the table
            if self.config['tables'] is True:
                table_jsons = self.process_tables(
                    soup, self.config['table_structure'], self.get_source_root(source)[:-1])

            output = {
                "source": source,
                "paragraphs": paragraphs,
                "tables": table_jsons
            }

            # write to output
            output_path = self.get_output_path(
                source)
            self.write_json(output, output_path)

    def process_files(self):
        for path in self.config['input_paths']:
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
