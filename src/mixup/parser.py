"""
Parse database file (see docs/db-sample.txt)
"""

from .core import ClassSkill, PlayerInfo


def _is_medic_only(class_string):
    return class_string in ('medic only', 'medic_only')


def _parse_classes_token(token):
    return set(map(str.lower, map(str.strip, token.split(','))))


def _parse_line(line_text):
    tokens = [t for t in line_text.split('\t') if t != '']
    skill = tokens[0].lower()
    nickname = tokens[1]
    main_class = tokens[2].lower()

    if len(tokens) < 4:
        additional_classes = set()
    else:
        additional_classes = _parse_classes_token(tokens[3])
        # Idiots check #1
        if main_class in additional_classes:
            additional_classes.remove(main_class)

    classes = set()
    if _is_medic_only(main_class):
        if skill == PlayerInfo.PREM:
            raise Exception('Prem player can not be "medic only"')
        else:
            classes.add(ClassSkill(ClassSkill.MEDIC, ClassSkill.MAIN))
    else:
        nonmain_classes = ClassSkill.CLASSES.difference(additional_classes)
        nonmain_classes.remove(main_class)

        # Open players should not play nonmain classes
        if skill != 'open':
            for c in nonmain_classes:
                classes.add(ClassSkill(c, ClassSkill.NONMAIN))

        for c in additional_classes:
            classes.add(ClassSkill(c, ClassSkill.ADDITIONAL))

        if skill != PlayerInfo.PREM:
            classes.add(ClassSkill(main_class, ClassSkill.MAIN))

    info = PlayerInfo(nickname, skill, tuple(classes))
    return info


def _parse_text(text):
    for line in text.split('\n'):
        if not line.startswith('//'):
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
