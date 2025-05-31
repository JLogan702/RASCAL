import pandas as pd
from jinja2 import Environment, FileSystemLoader
import json
import os

# Load CSV data
df = pd.read_csv("docs/jira_data.csv")

# Normalize column names
df.columns = [c.strip() for c in df.columns]

# Map components to teams
teams = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

# Define readiness statuses
readiness_statuses = ["Ready for Development", "To Do"]

# Filter to stories in future sprints only
df = df[
    (df["Issue Type"] == "Story") &
    (~df["Sprint"].fillna("").str.lower().str.contains("active")) &
    (df["Status"] != "Done") &
    (df["Components"].isin(teams.keys()))
]

# Prepare team data
team_data = {}

for component, label in teams.items():
    team_df = df[df["Components"] == component]
    status_counts = team_df["Status"].value_counts().to_dict()
    total = sum(status_counts.values())
    ready = sum(status_counts.get(s, 0) for s in readiness_statuses)
    percent = int((ready / total) * 100) if total > 0 else 0

    # Determine stoplight
    if percent >= 80:
        light = "blinking_green.gif"
    elif percent >= 50:
        light = "blinking_yellow.gif"
    else:
        light = "blinking_red.gif"

    team_data[label] = {
        "stoplight": light,
        "ready": ready,
        "total": total,
        "percent": percent,
        "status_breakdown": status_counts,
        "explanation": f"{ready} of {total} story tickets in this team's upcoming sprint are in a 'Ready' status ({percent}%)."
    }

# Jinja2 template render
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sprint_readiness_template.html")

output = template.render(team_data=team_data)

with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ sprint_readiness.html created.")

