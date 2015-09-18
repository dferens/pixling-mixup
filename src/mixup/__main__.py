import argparse

from .parser import parse_file
from .core import make_teams
from .ui import display_build


def main(db_file_path):
    players = parse_file(db_file_path)
    build = make_teams(players)
    display_build(build)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('db-file')
    args = parser.parse_args()
    main(getattr(args, 'db-file'))
