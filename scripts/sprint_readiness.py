import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load CSV
csv_path = "docs/jira_data.csv"
df = pd.read_csv(csv_path)

# Filter only story tickets in future sprints
future_sprint_mask = df['Sprint'].notna() & ~df['Sprint'].str.lower().str.contains("closed|completed|ended", na=False)
story_mask = df['Issue Type'] == 'Story'
status_mask = df['Status'].isin(['To Do', 'Ready for Development'])

filtered = df[future_sprint_mask & story_mask]

# Group and calculate readiness
readiness_data = []
components = filtered['Components'].dropna().unique()
for team in sorted(components):
    team_df = filtered[filtered['Components'] == team]
    total_stories = len(team_df)
    ready_stories = len(team_df[status_mask])
    percent_ready = (ready_stories / total_stories) * 100 if total_stories > 0 else 0

    if percent_ready >= 80:
        stoplight = "blinking_green.gif"
    elif percent_ready >= 50:
        stoplight = "blinking_yellow.gif"
    else:
        stoplight = "blinking_red.gif"

    breakdown = team_df['Status'].value_counts().to_dict()

    readiness_data.append({
        "team": team,
        "total": total_stories,
        "ready": ready_stories,
        "percent": round(percent_ready, 1),
        "stoplight": stoplight,
        "breakdown": breakdown
    })

# Setup Jinja2
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sprint_readiness_template.html")

# Render HTML
output = template.render(readiness_data=readiness_data)
with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ sprint_readiness.html generated.")

