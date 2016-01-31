"""
Parse database file (see docs/db-sample.txt)
"""
import re
from .core import ClassSkill, PlayerInfo

SCOUT_PATTERN = re.compile('scout')
SOLDIER_PATTERN = re.compile('soldier')
DEMOMAN_PATTERN = re.compile('demoman')
MEDIC_PATTERN = re.compile('medic')


def _is_single_class_player(class_token):
    return 'only' in class_token


def _get_class_name(class_token):
    if SCOUT_PATTERN.match(class_token):
        return ClassSkill.SCOUT
    elif SOLDIER_PATTERN.match(class_token):
        return ClassSkill.SOLDIER
    elif DEMOMAN_PATTERN.match(class_token):
        return ClassSkill.DEMOMAN
    elif MEDIC_PATTERN.match(class_token):
        return ClassSkill.MEDIC
    else:
        raise Exception('Invalid class: %s' % class_token)


def _parse_classes_token(token):
    tokens = map(str.lower, map(str.strip, token.split(',')))
    return set(map(_get_class_name, tokens))


def _parse_line(line_text):
    """
    Parses line of players list.
    Line is tab separated string of tokens - skill, nickname, main class
    and string of additional classes which may be empty.

    Some notes on classes:
        - Players can choose 'scout', 'soldier', 'demoman' and 'medic' classes.
        - Players can add 'only' string to main class so they will play only
          one class.
        - Prem tier players are available to play their main classes only within
          'only' mode (see prev note).
    """
    tokens = [t for t in line_text.split('\t') if t != '']
    skill = tokens[0].lower()
    nickname = tokens[1]
    main_class_token = tokens[2].lower()
    main_class = _get_class_name(main_class_token)
    classes = set()

    if _is_single_class_player(main_class_token):
        classes.add(ClassSkill(main_class, ClassSkill.MAIN))
    else:
        if len(tokens) < 4:
            additional_classes = set()
        else:
            additional_classes = _parse_classes_token(tokens[3])
            # Idiots check #1
            if main_class in additional_classes:
                additional_classes.remove(main_class)

        if skill != PlayerInfo.PREM:
            classes.add(ClassSkill(main_class, ClassSkill.MAIN))

        for c in additional_classes:
            classes.add(ClassSkill(c, ClassSkill.ADDITIONAL))

        # Open players should play main and additional classes only
        if skill != 'open':
            nonmain_classes = ClassSkill.CLASSES.difference(additional_classes)
            nonmain_classes.remove(main_class)
            for c in nonmain_classes:
                classes.add(ClassSkill(c, ClassSkill.NONMAIN))

    info = PlayerInfo(nickname, skill, tuple(classes))
    return info


def _parse_text(text):
    for line in text.split('\n'):
        if not line.startswith('//') and line != '':
            yield _parse_line(line)


def parse_file(file_path):
    """
    Parses database file

    @param str file_path
    @rtype list[PlayerInfo]
    """
    with open(file_path) as f:
        text = f.read()

    return list(_parse_text(text))
