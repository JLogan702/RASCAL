import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Set path to templates directory relative to this script
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("backlog_health_template.html")

# Load Jira CSV
df = pd.read_csv("../docs/jira_data.csv")

# Filter for story tickets in backlog-valid statuses
valid_statuses = ["New", "Grooming", "Backlog"]
df = df[(df["Issue Type"] == "Story") & (df["Status"].isin(valid_statuses))]

# Assign teams from Components (assumes Components maps 1:1 to teams)
df["Team"] = df["Components"].fillna("Unknown")

# Summarize status counts by team
summary = {}
for team, group in df.groupby("Team"):
    total = len(group)
    status_counts = group["Status"].value_counts().to_dict()
    relevant = status_counts.get("New", 0) + status_counts.get("Grooming", 0) + status_counts.get("Backlog", 0)
    percent_ready = int((relevant / total) * 100) if total else 0

    # Determine stoplight color
    if percent_ready >= 80:
        stoplight = "blinking_green.gif"
    elif percent_ready >= 50:
        stoplight = "blinking_yellow.gif"
    else:
        stoplight = "blinking_red.gif"

    summary[team] = {
        "total": total,
        "status_counts": status_counts,
        "percent_ready": percent_ready,
        "stoplight": stoplight
    }

# Render HTML
output = template.render(summary=summary)

# Save output
with open("../docs/backlog_health.html", "w") as f:
    f.write(output)

print("✅ Backlog Health dashboard generated.")

