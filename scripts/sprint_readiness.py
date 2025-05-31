import pandas as pd
import json
from jinja2 import Environment, FileSystemLoader

# Load Jira data
df = pd.read_csv("docs/jira_data.csv")

# Filter for story tickets in future sprints, excluding Done or active sprint
valid_statuses = ["Ready for Development", "To Do"]
ignore_statuses = ["Done", "Blocked", "Cancelled", "In Progress"]
df = df[df["Issue Type"] == "Story"]
df = df[~df["Status"].isin(ignore_statuses)]

# Ensure Sprint filtering (sprint field exists and is not in open sprints)
df = df[df["Sprint"].notna()]
df = df[df["Sprint"].str.contains("state=FUTURE", na=False)]

# Normalize team values
df["Components"] = df["Components"].fillna("Unassigned")

# Calculate readiness per team
teams = []
for team_name in df["Components"].unique():
    team_df = df[df["Components"] == team_name]
    total = len(team_df)
    ready = team_df["Status"].isin(valid_statuses).sum()
    percent = (ready / total) * 100 if total > 0 else 0

    if percent >= 80:
        stoplight = "blinking_green.gif"
    elif percent >= 50:
        stoplight = "blinking_yellow.gif"
    else:
        stoplight = "blinking_red.gif"

    # Count all statuses in scope
    status_counts = team_df["Status"].value_counts().to_dict()

    teams.append({
        "name": team_name,
        "stoplight": stoplight,
        "percent": round(percent, 1),
        "status_counts": status_counts,
        "explanation": (
            f"{ready} of {total} story tickets are in 'Ready for Development' or 'To Do' status. "
            f"Tickets must be assigned to a future sprint and not be Done, In Progress, or Blocked to be included."
        )
    })

# Render HTML
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sprint_readiness_template.html")

output_html = template.render(teams=teams)

with open("docs/sprint_readiness.html", "w") as f:
    f.write(output_html)

print("✅ sprint_readiness.html generated successfully.")

