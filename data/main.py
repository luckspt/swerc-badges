import ast
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, cast

role_column = 'teamRolesOut'
roles_to_split_by_country = {'contestant', 'coach', 'reserve'}
unknown = 'unknown'

class PeopleRow(TypedDict, total=False):
    username: Optional[str]
    secondaryEmail: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    badgeName: Optional[str]
    title: Optional[str]
    sex: Optional[str]
    dob: Optional[str]
    phone: Optional[str]
    jobTitle: Optional[str]
    company: Optional[str]
    specialNeeds: Optional[str]
    shirtSize: Optional[str]
    registrationComplete: Optional[str]
    homeCountry: Optional[str]
    expectedGrad: Optional[str]
    beganDegree: Optional[str]
    includeEmail: Optional[str]
    employmentOpportunities: Optional[str]
    informOtherContests: Optional[str]
    addressLine1: Optional[str]
    addressLine2: Optional[str]
    addressLine3: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postalCode: Optional[str]
    twitter: Optional[str]
    facebook: Optional[str]
    topCoder: Optional[str]
    codeforces: Optional[str]
    linkedin: Optional[str]
    surname: Optional[str]
    givenNames: Optional[str]
    applyFromCity: Optional[str]
    passportCountry: Optional[str]
    visaPlan: Optional[str]
    passportNumber: Optional[str]
    passportExpiry: Optional[str]
    passportIssue: Optional[str]
    passportNationality: Optional[str]
    residenceCountry: Optional[str]
    residenceCity: Optional[str]
    passportNotNeeded: Optional[str]
    visaType: Optional[str]
    consulateCountry: Optional[str]
    consulateCity: Optional[str]
    consulateInterview: Optional[str]
    visaNeeded: Optional[str]
    entryAirport: Optional[str]
    instName: Optional[str]
    instShortName: Optional[str]
    instNativeName: Optional[str]
    teamIds: Optional[str]
    teamIdsOut: Optional[str]
    teams: Optional[str]
    teamsList: Optional[str]
    teamRoles: Optional[str]
    teamRolesOut: Optional[str]
    teamSites: Optional[str]
    teamSitesOut: Optional[str]
    workstationIds: Optional[str]
    workstationIdsOut: Optional[str]
    staffRoles: Optional[str]
    staffRolesOut: Optional[str]
    staffSites: Optional[str]
    staffSitesOut: Optional[str]
    localName: Optional[str]
    emergencyContact: Optional[str]
    emergencyPhone: Optional[str]

outputHeaders = [
    'Name',
    'Team',
    'University',
    'Role',
    'Country',
]
class OutputRow(TypedDict):
    Name: str
    Team: str
    University: str
    Role: str
    Country: str


class TeamRow(TypedDict, total=False):
    teamName: Optional[str]
    siteName: Optional[str]
    institutionName: Optional[str]
    created: Optional[str]
    status: Optional[str]
    eligibilityStatus: Optional[str]
    certified: Optional[str]
    paid: Optional[str]
    extendedState: Optional[str]
    country: Optional[str]
    coachName: Optional[str]
    IP: Optional[str]
    PC: Optional[str]

def parse_teams_field(s: Any) -> List[Dict[str, Any]]:
    """Parse a teams-like field from the CSV.

    Accepts JSON, Python-literal, or a bracketed single name. Returns a list
    of dicts or strings normalized to list format.
    """
    if not s:
        return []

    if isinstance(s, list):
        return s # type: ignore

    text = str(s).strip()

    # Try JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try python literal
    try:
        return ast.literal_eval(text)
    except Exception:
        pass

    # Fix doubled quotes that sometimes appear in CSV exports
    try:
        fixed = text.replace('""', '"')
        return json.loads(fixed)
    except Exception:
        pass

    # Fallback: single value inside brackets, e.g. [Team Name]
    if text.startswith('[') and text.endswith(']'):
        inner = text[1:-1].strip()
        if inner:
            if (inner.startswith('"') and inner.endswith('"')) or (
                inner.startswith("'") and inner.endswith("'")
            ):
                inner = inner[1:-1]
            return [{'id': None, 'name': inner}]

    return []


def load_teams(path: Path) -> Dict[str, TeamRow]:
    teams: Dict[str, TeamRow] = {}
    if not path.exists():
        return teams
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tr = cast(TeamRow, row)
            key = (tr.get('teamName') or '').strip()
            if not key:
                continue
            teams[key] = tr

    return teams

def get_role(row: PeopleRow) -> str:
    """Get the role of a person from the row based on the group_by field."""
    role = row.get(role_column)
    if not role:
        return unknown
    
    role = role.lower()
    
    if role == 'cocoach':
        return 'coach'
    
    if role == 'staff':
        return 'organizer'
    
    return role

def load_people(path: Path) -> List[PeopleRow]:
    """Load `all.csv` and return a list of typed rows (PeopleRow)."""
    rows: List[PeopleRow] = []
    if not path.exists():
        return rows
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = cast(PeopleRow, r)
            row[role_column] = get_role(row)
            rows.append(row)

    return rows


def group_people_by_role(people: List[PeopleRow]) -> Dict[str, List[PeopleRow]]:
    """Group people by their role (from `group_by` field)."""
    grouped: Dict[str, List[PeopleRow]] = {}
    for row in people:
        key = row.get(role_column) or ''
        grouped.setdefault(key, []).append(row)
    return grouped


def map_to_output(group: str, row: PeopleRow, teams: Dict[str, TeamRow]) -> OutputRow:
    teams_field = row.get('teams') or row.get('teamsList') or ''
    parsed = parse_teams_field(teams_field)

    team_name = unknown
    university = unknown
    country = unknown

    if parsed:
        first = parsed[0]
        team_name = first.get('name') or str(first.get('id') or unknown)
        team_name = team_name.strip()

        # Lookup institution from teams.csv by team name
        if team_name in teams:
            university = str(teams[team_name].get('institutionName') or unknown)
            country = str(teams[team_name].get('country') or unknown)
        else:
            tn = team_name.strip()
            if tn in teams:
                university = str(teams[tn].get('institutionName') or unknown)
                country = str(teams[tn].get('country') or unknown)

    name = ((row.get('firstName') or '') + ' ' + (row.get('lastName') or '')).strip()
    return {
        'Name': name,
        'Team': team_name or unknown,
        'University': university or unknown,
        'Role': group or unknown,
        'Country': country or unknown,
    }


def write_grouped_people(group: str, people: List[OutputRow], out_dir: Path) -> None:
    out_path = out_dir / f'{group}.csv'
    with out_path.open('w', newline='', encoding='utf-8') as f:
        # Write header of the CSV file
        writer = csv.DictWriter(f, fieldnames=outputHeaders)
        writer.writeheader()
        writer.writerows(people)

def split_by_country(people: List[OutputRow]) -> Dict[str, List[OutputRow]]:
    countries: Dict[str, List[OutputRow]] = {}
    for person in people:
        country = person.get('Country') or unknown
        countries.setdefault(country, []).append(person)
    
    return countries

def process(all_csv: Path, teams_csv: Path, out_dir: Path) -> None:
    teams = load_teams(teams_csv)
    people = load_people(all_csv)
    grouped = group_people_by_role(people)

    for group, people in grouped.items():
        mapped = [map_to_output(group, person, teams) for person in people]

        if roles_to_split_by_country and group in roles_to_split_by_country:
            countries = split_by_country(mapped)
            for country, country_people in countries.items():
                country_dir = out_dir / country
                country_dir.mkdir(exist_ok=True)

                write_grouped_people(group, country_people, country_dir)
        else:
            write_grouped_people(group, mapped, out_dir)
    

def stats() -> None:
    """
    Longest and shortest names, teams, universities; countries represented.
    """

def main() -> None:
    base = Path(__file__).parent
    all_csv = base / 'all.csv'
    teams_csv = base / 'teams.csv'
    out_dir = base / 'output'
    out_dir.mkdir(exist_ok=True)
    process(all_csv, teams_csv, out_dir)


if __name__ == '__main__':
    main()