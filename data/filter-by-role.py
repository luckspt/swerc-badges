import csv
from typing import List, Dict
import json
import ast

group_by = 'teamRolesOut'

# load teams.csv keyed by team name -> institution, country
teams = {}
with open('teams.csv', 'r') as f:
    reader = csv.DictReader(f)
    teams = {
        row['teamName']: {
            'institution': row.get('institutionName', ''),
            'country': row.get('country', '')
        } for row in reader
    }


def parse_teams_field(s: str) -> List[Dict[str, str]]:
    """Parse the `teams` column from all.csv which is a JSON-ish string like
    '[{"id": 123, "name": "Some team"}]'.

    Try json.loads, then ast.literal_eval, then try fixing doubled
    quotes which can appear due to CSV quoting.
    Returns a list of team dicts or an empty list.
    """
    if not s:
        return []

    # If it's already a list/object, return as-is
    if isinstance(s, list):
        return s

    # Trim whitespace
    s = s.strip()

    # Try JSON first
    try:
        return json.loads(s)
    except Exception:
        pass

    # Try ast.literal_eval (accepts python-like lists/dicts)
    try:
        return ast.literal_eval(s)
    except Exception:
        pass

    # Sometimes CSV double-quotes are doubled (""), try to fix
    try:
        fixed = s.replace('""', '"')
        return json.loads(fixed)
    except Exception:
        pass

    # As a last resort, try to extract a single team name from square-bracket form
    # like [Team Name] (non-JSON). We'll return a list with one dict with name only.
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        if inner:
            # remove surrounding quotes if present
            if (inner.startswith('"') and inner.endswith('"')) or (inner.startswith("'") and inner.endswith("'")):
                inner = inner[1:-1]
            return [{'id': None, 'name': inner}]

    return []


with open('all.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = sorted(reader, key=lambda x: x.get('firstName', ''))

    out = {}
    for row in data:
        key = row.get(group_by, '')
        out.setdefault(key, []).append(row)

    for group, users in out.items():
        print(f'{group}: {len(users)}')

        with open(f'{group}.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=('Name', 'Team', 'University', 'Role', 'Country'))
            writer.writeheader()

            for row in users:
                # Parse the teams column (prefer 'teams' which contains id+name)
                teams_field = row.get('teams') or row.get('teamsList') or ''
                parsed = parse_teams_field(teams_field)

                team_name = 'N/A'
                university = 'N/A'
                country = 'N/A'

                if parsed:
                    # parsed is expected to be a list of dicts like {"id":..., "name":...}
                    first = parsed[0]
                    if isinstance(first, dict):
                        team_name = first.get('name') or str(first.get('id') or 'N/A')
                    else:
                        # sometimes it's just a string
                        team_name = str(first)

                    team_name = team_name.strip()

                    # Lookup institution from teams.csv by team name
                    if team_name in teams:
                        university = teams[team_name].get('institution', 'N/A')
                        country = teams[team_name].get('country', 'N/A')
                    else:
                        # fallback: maybe name has extra whitespace
                        tn = team_name.strip()
                        if tn in teams:
                            university = teams[tn].get('institution', 'N/A')
                            country = teams[tn].get('country', 'N/A')
                        else:
                            university = 'N/A'
                            country = 'N/A'

                writer.writerow({
                    'Name': (row.get('firstName', '') + ' ' + row.get('lastName', '')).strip(),
                    'Team': team_name,
                    'University': university,
                    'Role': group,
                    'Country': country
                })
