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

with open('Contestant.csv', 'r') as f:
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

        with open(f'{group}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in users:
                writer.writerow(row)
