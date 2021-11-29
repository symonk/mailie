import argparse

from ._configuration import Configuration


def build_configuration() -> Configuration:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
    )
    return Configuration(**vars(parser.parse_args()))
