"""
The most advanced UI in the world.
"""
from .core import Team, TeamsBuild, PlayerInfo


def get_team_print_info(team):
    """
    Returns team info as string.

    @param core.Team team
    @rtype str
    """
    assert isinstance(team, Team)
    result = ''
    pattern = '{nickname}[{skill}]: {game_class}\n'

    order = {
        PlayerInfo.PREM: 0,
        PlayerInfo.HIGH: 1,
        PlayerInfo.MID: 2,
        PlayerInfo.OPEN: 4
    }

    for p in sorted(team.get_players(), key=lambda p: order[p.skill]):
        result += pattern.format(
            nickname=p.nickname,
            skill=p.skill,
            game_class=team.get_player_class(p)
        )
    result += 'Strength: {}\n'.format(team.calc_strength())
    return result


def _get_build_print_info(build):
    """
    Returns total build info as string.

    @param core.TeamsBuild build
    @rtype str
    """
    assert isinstance(build, TeamsBuild)

    result = ''
    for i, team in enumerate(build.teams):
        result += 'Team #{}\n'.format(i + 1)
        result += get_team_print_info(team)
        result += '\n'

    used_amount, remaining_count = build.calc_utilization_info()
    result += (
        'Used {} % of players ({} are waiting)'.format(
            int(used_amount * 100), remaining_count
        )
    )
    result += '\n'
    result += (
        'Waiting list: {}'.format(
            ', '.join(p.nickname for p in build.remaining_players)
        )
    )
    result += '\n'
    min_strength, max_strength, variance = build.calc_strength_info()
    result += (
        'Strength: min={:.2f}, max={:.2f}, variance={:.5}'.format(
            min_strength, max_strength, variance
        )
    )
    return result


def display_build(build):
    print(_get_build_print_info(build))
