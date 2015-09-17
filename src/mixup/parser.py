"""
Parse database file (see docs/db-sample.txt)
"""

class ClassSkill:
    """
    Describes player's ability to play given class.
    """
    __slots__ = ('_class', '_type')

    SOLDIER = 'soldier'
    SCOUT = 'scout'
    MEDIC = 'medic'
    DEMOMAN = 'demoman'
    CLASSES = set((SOLDIER, SCOUT, MEDIC, DEMOMAN))

    MAIN = 'main'
    ADDITIONAL = 'additional'
    NONMAIN = 'nonmain'
    TYPES = set((MAIN, ADDITIONAL, NONMAIN))

    def __init__(self, class_, type):
        assert class_ in self.CLASSES
        assert type in self.TYPES
        self._class = class_
        self._type = type

    def __repr__(self):
        return '{}={}'.format(
            self._class.upper(),
            self._type
        )

    @property
    def game_class(self):
        return self._class

    @property
    def type(self):
        return self._type


class PlayerInfo:

    __slots__ = ('_nickname', '_skill', '_classes')

    PREM = 'prem'
    HIGH = 'high'
    MID = 'mid'
    OPEN = 'open'
    SKILLS = set((PREM, HIGH, MID, OPEN))

    def __init__(self, nickname, skill, classes):
        assert skill in self.SKILLS
        self._nickname = nickname
        self._skill = skill
        self._classes = tuple(classes)

    def __repr__(self):
        classes_str = ', '.join(repr(c) for c in self._classes)
        return '<PlayerInfo {0} [{1}] {2}>'.format(
            self._nickname,
            self._skill.upper(),
            classes_str
        )

    @property
    def nickname(self):
        return self._nickname

    @property
    def skill(self):
        return self._skill

    @property
    def classes(self):
        return self._classes



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

    classes = set()
    if _is_medic_only(main_class):
        classes.add(ClassSkill(ClassSkill.MEDIC, ClassSkill.MAIN))
    else:
        classes.add(ClassSkill(main_class, ClassSkill.MAIN))
        for c in additional_classes:
            classes.add(ClassSkill(c, ClassSkill.ADDITIONAL))

        for c in ClassSkill.CLASSES.difference(classes):
            classes.add(ClassSkill(c, ClassSkill.NONMAIN))

    info = PlayerInfo(nickname, skill, classes)
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
