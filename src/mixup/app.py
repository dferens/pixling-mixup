from .parser import parse_file
from .core import make_teams
from .ui import display_build


def main():
    players = parse_file('docs/db-sample.txt')
    build = make_teams(players)
    display_build(build)


if __name__ == '__main__':
    main()
