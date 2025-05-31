import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load and filter the data
df = pd.read_csv("docs/jira_data.csv")

# Clean up column names just in case
df.columns = df.columns.str.strip()

# Only keep Story tickets with valid backlog statuses
valid_statuses = ["New", "Grooming", "Backlog"]
df = df[(df["Issue Type"] == "Story") & (df["Status"].isin(valid_statuses))]

# Remove issues that are assigned to active sprints
df = df[df["Sprint"].isna() | ~df["Sprint"].str.contains("state=ACTIVE", na=False)]

# Group by Component
teams = df["Components"].dropna().unique()
team_data = []

for team in teams:
    team_df = df[df["Components"] == team]
    status_counts = team_df["Status"].value_counts().to_dict()

    total_stories = sum(status_counts.values())
    backlog_stories = sum([status_counts.get(status, 0) for status in valid_statuses])
    backlog_score = (backlog_stories / total_stories) * 100 if total_stories > 0 else 0

    if backlog_score >= 80:
        light = "blinking_green.gif"
    elif backlog_score >= 50:
        light = "blinking_yellow.gif"
    else:
        light = "blinking_red.gif"

    team_data.append({
        "team": team,
        "total_stories": total_stories,
        "backlog_stories": backlog_stories,
        "status_counts": status_counts,
        "backlog_score": round(backlog_score),
        "stoplight": light
    })

# Sort alphabetically by team name
team_data = sorted(team_data, key=lambda x: x["team"])

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("backlog_health_template.html")

# Render the page
output = template.render(team_data=team_data)

# Write to file
with open("docs/backlog_health.html", "w") as f:
    f.write(output)

print("✅ backlog_health.html generated.")

