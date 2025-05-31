import pandas as pd
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

# Load the Jira data
df = pd.read_csv("docs/jira_data.csv")

# Ensure no NaNs
inward_blocks = df['Inward issue link (Blocks)'].fillna('')
outward_blocks = df['Outward issue link (Blocks)'].fillna('')

# Parse team from component
team_map = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

df['Team'] = df['Components'].map(team_map)

# Aggregate dependencies by team
dependencies = defaultdict(lambda: {"blocks": 0, "blocked_by": 0})

for _, row in df.iterrows():
    team = row['Team']
    if not team:
        continue

    if row['Inward issue link (Blocks)']:
        dependencies[team]['blocked_by'] += 1
    if row['Outward issue link (Blocks)']:
        dependencies[team]['blocks'] += 1

# Calculate totals and stoplight color
summary = []
for team, data in dependencies.items():
    total = data['blocks'] + data['blocked_by']
    if total == 0:
        color = "green"
    elif data['blocked_by'] > data['blocks']:
        color = "red"
    else:
        color = "yellow"
    summary.append({
        "team": team,
        "blocks": data['blocks'],
        "blocked_by": data['blocked_by'],
        "total": total,
        "color": color
    })

# Sort by team name
summary.sort(key=lambda x: x['team'])

# Render HTML
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")
output = template.render(summary=summary)

with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html updated")

