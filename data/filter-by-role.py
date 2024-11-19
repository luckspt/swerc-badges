import csv

with open('all.csv', 'r') as f:
    reader = csv.DictReader(f)

    roles = dict()
    for row in reader:
        if row['role'] not in roles:
            roles[row['role']] = []

        roles[row['role']].append(row)

    for role, user in roles.items():
        print(f'{role}: {len(user)}')

        with open(f'{role}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in user:
                writer.writerow(row)