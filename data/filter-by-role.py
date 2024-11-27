import csv

group_by = 'role'

with open('all.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = sorted(filter(lambda x: x['teamStatus'].lower() == 'accepted',reader), key=lambda x: x['firstName'])

    out = dict()
    for row in data:
        if row[group_by] not in out:
            out[row[group_by]] = []

        out[row[group_by]].append(row)

    for group, users in out.items():
        print(f'{group}: {len(users)}')

        with open(f'{group}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=('Name', 'Team', 'University', 'Role'))
            writer.writeheader()

            for row in users:
                writer.writerow({
                    'Name': row['firstName'] + ' ' + row['lastName'],
                    'Team': row['teamName'],
                    'University': row['instName'],
                    'Role': group
                })
