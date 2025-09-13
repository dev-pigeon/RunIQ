import argparse
import json


class Pipeline:
    def __init__(self) -> None:
        pass

    def run(self, config):
        # config = json with N processing groups / is a list of objects
        for group in config:
            print(group)
            pass
        pass


if __name__ == "__main__":
    # get the path to the config file
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config-path', help="Path to the config file for the vectorization pipeline.")
    args = parser.parse_args()
    config_path = args.config_path

    with open(config_path, 'r') as file:
        config = json.load(file)

    print("Beginning vectorization pipeline.")
    pipeline = Pipeline()
    pipeline.run(config)
