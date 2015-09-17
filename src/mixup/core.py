from statistics import variance
from random import choice as rand_choice


class ClassSkill:
    """
    Describes player's ability to play given class.

    Should be immutable (value object).
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

    def __hash__(self):
        return hash((self._class, self._type))

    def __eq__(self, other):
        return (
            self._class == other._class and
            self._type == other._type
        )

    @property
    def game_class(self):
        return self._class

    @property
    def type(self):
        return self._type


class PlayerInfo:
    """
    Describes player.

    Should be immutable (value object).
    """

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
        self._classes = classes

    def __repr__(self):
        classes_str = ', '.join(repr(c) for c in self._classes)
        return '<PlayerInfo {0} [{1}] {2}>'.format(
            self._nickname,
            self._skill.upper(),
            classes_str
        )

    def __hash__(self):
        return hash((self._nickname, self._skill, self._classes))

    @property
    def nickname(self):
        return self._nickname

    @property
    def skill(self):
        return self._skill

    @property
    def classes(self):
        return self._classes

    def get_class_type(self, game_class):
        skill = None
        for s in self._classes:
            if s.game_class == game_class:
                skill = s
                break
        else:
            raise Exception('This player can not play such class: ' + game_class)

        return skill.type

    def get_variability(self):
        """
        Returns number of player's classes he can play easily.

        @rtype int
        """
        active_classes = [c for c in self._classes if c.type != c.NONMAIN]
        return len(active_classes)

    def calc_strength(self, game_class):
        """
        Specific metric which indicates how strong player is on given class.

        @param str game_class
        @rtype float
        """
        # 1. Prem player playing additional class should be ~= high player
        # playing main, while prem player playing nonmain should be ~= high
        # player playing additional class.
        # Same applies for (high, mid) and (mid, open) pairs.
        TYPE_COEFFS = {
            ClassSkill.MAIN: 1,
            ClassSkill.ADDITIONAL: 0.75,
            ClassSkill.NONMAIN: 0.4
        }
        SKILL_STRENGTH = {
            self.PREM: 16,
            self.HIGH: 8,
            self.MID: 4,
            self.OPEN: 2,
        }
        class_type = TYPE_COEFFS[self.get_class_type(game_class)]
        return SKILL_STRENGTH[self.skill] * class_type

    def get_preferred_class_seq(self):
        """
        Returns preferred player's game class sequence.
        First item is the most preferred, second one is less and so on.

        @rtype list(str)
        """
        order = {
            ClassSkill.MAIN: 0,
            ClassSkill.ADDITIONAL: 1,
            ClassSkill.NONMAIN: 2
        }
        sorted_classes = sorted(self._classes, key=lambda c: order[c.type])
        return [c.game_class for c in sorted_classes]


class Team:
    CLASS_LIMIT = {
        ClassSkill.SOLDIER: 2,
        ClassSkill.SCOUT: 2,
        ClassSkill.MEDIC: 1,
        ClassSkill.DEMOMAN: 1
    }
    MAX_PLAYER_COUNT = sum(CLASS_LIMIT.values())

    def __init__(self, id):
        self._id = id
        self._game_classes = {}

    @property
    def id(self):
        """
        Team identifier.

        @rtype object
        """
        return self._id

    def copy(self):
        result =  type(self)(self._id)
        result._game_classes = dict(self._game_classes)
        return result

    def get_players(self):
        return self._game_classes.keys()

    def set_player_class(self, player, game_class):
        if player not in self._game_classes:
            if len(self._game_classes) == self.MAX_PLAYER_COUNT:
                raise Exception('Team is full')

        self._game_classes[player] = game_class

    def clear_player(self, player):
        del self._game_classes[player]

    def get_player_class(self, player):
        return self._game_classes[player]

    def is_class_available(self, game_class):
        slots_taken = filter(lambda c: c == game_class, self._game_classes.values())
        slots_remaining = self.CLASS_LIMIT[game_class] - len(list(slots_taken))
        return slots_remaining > 0

    def calc_strength(self):
        """
        Calculates team's overal strength.
        """
        return sum(
            p.calc_strength(game_class)
            for p, game_class in self._game_classes.items()
        )


class TeamsBuild:

    @classmethod
    def make_initial(cls, players):
        teams = []
        ids = {'team': 0}

        def make_team():
            result = Team(ids['team'])
            ids['team'] += 1
            return result

        #
        # Step 1: add prem players
        #
        prem_players = set(p for p in players if p.skill == p.PREM)

        for p in prem_players:
            new_team = make_team()
            preferred_class = p.get_preferred_class_seq()[0]
            new_team.set_player_class(p, preferred_class)
            teams.append(new_team)

        remaining_players = players.difference(prem_players)
        build = cls(teams, remaining_players)

        #
        # Step 2: add other players, start with single-class ones
        #
        ordered_players = sorted(remaining_players, key=PlayerInfo.get_variability)
        for p in ordered_players:
            preferred_class = p.get_preferred_class_seq()[0]
            for t in teams:
                if t.is_class_available(preferred_class):
                    build.pop_remaining(p, t, preferred_class)
                    break

        #
        # Step 3: create teams from remaining players
        #
        remaining_count = len(build.remaining_players)
        new_full_teams_count = int(remaining_count / Team.MAX_PLAYER_COUNT)
        remaining_teams = []
        for i in range(new_full_teams_count):
            new_team = make_team()
            remaining_teams.append(new_team)
            build.add_team(new_team)

        #
        # Step 4: fill remaining teams
        #
        ordered_players = sorted(build.remaining_players, key=PlayerInfo.get_variability)
        for p in ordered_players:
            for preferred_class in p.get_preferred_class_seq():
                found_team = False
                for t in remaining_teams:
                    if t.is_class_available(preferred_class):
                        build.pop_remaining(p, t, preferred_class)
                        found_team = True
                        break

                if found_team:
                    break

        return build

    def __init__(self, teams, remaining_players):
        self._teams = teams
        self._remaining_players = remaining_players

    def copy(self):
        """
        Creates deep copy of itself.

        @rtype TeamsBuild
        """
        return type(self)(
            list(t.copy() for t in self._teams),
            set(self._remaining_players)
        )

    @property
    def teams(self):
        return tuple(self._teams)

    def get_team(self, team_id):
        for t in self._teams:
            if t.id == team_id:
                return t
        else:
            raise IndexError('Given team not found: ' + team_id)

    @property
    def remaining_players(self):
        return tuple(self._remaining_players)

    def add_team(self, team):
        self._teams.append(team)

    def calc_utilization_info(self):
        """
        Returns players untilization info.

        @returns (used_amount, remaining_count)
        @rtype tuple(float, int)
        """
        used_count = sum(
            len(t.get_players())
            for t in self._teams
        )
        remaining_count = len(self._remaining_players)
        total_players = used_count + remaining_count
        return (used_count / total_players, remaining_count)

    def calc_strength_info(self):
        """
        Returns total teams strength info.

        @rtype tuple(float, float, float)
        @returns (min, max, variance)
        """
        vals = [t.calc_strength() for t in self._teams]
        return (
            min(vals),
            max(vals),
            variance(vals)
        )

    def pop_remaining(self, player, target_team, game_class):
        """
        Moves player from `remaining` player pool to specific team to play
        given class.

        @param PlayerInfo player
        @param Team target_team
        @param str game_class
        """
        self._remaining_players.remove(player)
        target_team.set_player_class(player, game_class)


class SwapTransaction:
    """
    Simple transaction which swaps 2 players in 2 different teams.
    """
    def __init__(self, team_from_id, player_from, team_to_id, player_to):
        self._team_from = team_from_id
        self._player_from = player_from
        self._team_to = team_to_id
        self._player_to = player_to

    def apply(self, build):
        """
        Modifies build in place.
        Applies transaction to build, changes player positions inside teams.

        @param TeamsBuild build
        """
        team_from = build.get_team(self._team_from)
        team_to = build.get_team(self._team_to)
        player_from_class = team_from.get_player_class(self._player_from)
        player_to_class = team_to.get_player_class(self._player_to)
        team_from.clear_player(self._player_from)
        team_to.clear_player(self._player_to)
        team_from.set_player_class(self._player_to, player_from_class)
        team_to.set_player_class(self._player_from, player_to_class)


def gen_transactions(build, team_from, team_to):
    for player_from in team_from.get_players():
        game_class = team_from.get_player_class(player_from)
        player_from_strength = player_from.calc_strength(game_class)

        for player_to in team_to.get_players():
            if team_to.get_player_class(player_to) == game_class:
                if player_from_strength > player_to.calc_strength(game_class):
                    yield SwapTransaction(
                        team_from.id, player_from,
                        team_to.id, player_to
                    )


def _shuffle_step(build):
    # Cache calculated strengths
    strengths = {t: t.calc_strength() for t in build.teams}
    sorted_teams = sorted(build.teams, key=strengths.__getitem__)
    weakest_team, *other, strongest_team = sorted_teams
    transactions = gen_transactions(build, strongest_team, weakest_team)
    solutions = {}

    for t in transactions:
        new_build = build.copy()
        t.apply(new_build)
        new_weakest_strength = new_build.get_team(weakest_team.id).calc_strength()
        new_strongest_strength = new_build.get_team(strongest_team.id).calc_strength()
        strength_diff = abs(new_weakest_strength - new_strongest_strength)
        solutions[new_build] = strength_diff

    best_build, _ = min(solutions.items(), key=lambda keyval: keyval[1])
    return best_build


def make_teams(players):
    """
    Forms list of teams.

    @param list[parser.PlayerInfo] players
    @rtype TeamsBuild
    """
    assert all(isinstance(p, PlayerInfo) for p in players)

    players = set(players)
    initial_build = TeamsBuild.make_initial(players)

    # Minimize strength variance
    target_fn = lambda b: b.calc_strength_info()[2]

    current_build = initial_build
    current_target = target_fn(current_build)
    print('Initial target: ', current_target)

    while True:
        new_build = _shuffle_step(current_build)
        new_target = target_fn(new_build)
        print('New target: ', new_target)

        if new_target < current_target:
            current_build = new_build
            current_target = new_target
        else:
            break

    return current_build
