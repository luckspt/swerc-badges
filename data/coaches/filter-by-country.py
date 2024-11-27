import csv

teams = dict()
totalTeams = 0
with open('teams.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        totalTeams += 1
        teams[row['teamName']] = row['country']

if len(teams) != totalTeams:
    print('SOME TEAM HAS A DUPE NAME')
    exit()

### ------
def getTeamCountry(row):
    return teams[row['Team']]

with open('Coach.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = sorted(reader, key=lambda x: x['Team'])

    out = dict()
    for row in data:
        country = getTeamCountry(row)
        if country not in out:
            out[country] = []

        out[country].append(row)

    for group, users in out.items():
        print(f'{group}: {len(users)}')

        coach_teams = dict()
        for coach in users:
            if coach['Name'] not in coach_teams:
                coach_teams[coach['Name']] = {'Team': [], 'University': coach['University'], 'Role': coach['Role']}

            coach_teams[coach['Name']]['Team'].append(coach['Team'])
        

        with open(f'{group}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()

            for coach in coach_teams.keys():
                writer.writerow({
                    'Name': coach,
                    'Team': ' || '.join(coach_teams[coach]['Team']),
                    'University': coach_teams[coach]['University'],
                    'Role': coach_teams[coach]['Role'],
                })
