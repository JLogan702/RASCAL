import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load Jira CSV data
df = pd.read_csv("docs/jira_data.csv")

# Filter only story tickets that have actual blocking dependencies
df = df[df["Issue Type"] == "Story"]
df = df[df["Inward issue link (Blocks)"].notnull() | df["Outward issue link (Blocks)"].notnull()]

# Create dependency rows
records = []
for _, row in df.iterrows():
    issue_key = row["Issue key"]
    summary = row.get("Summary", "N/A")
    team = row.get("Components", "Unassigned")

    if pd.notnull(row.get("Inward issue link (Blocks)")):
        linked_keys = str(row["Inward issue link (Blocks)"]).split(", ")
        for lk in linked_keys:
            records.append({
                "team": team,
                "issue_key": issue_key,
                "summary": summary,
                "linked_issue": lk.strip(),
                "link_type": "Blocked by"
            })

    if pd.notnull(row.get("Outward issue link (Blocks)")):
        linked_keys = str(row["Outward issue link (Blocks)"]).split(", ")
        for lk in linked_keys:
            records.append({
                "team": team,
                "issue_key": issue_key,
                "summary": summary,
                "linked_issue": lk.strip(),
                "link_type": "Blocking"
            })

# Group by team
dependencies_by_team = {}
for record in records:
    team = record["team"]
    dependencies_by_team.setdefault(team, []).append(record)

# Jinja2 setup
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")

# Render HTML
output = template.render(dependencies_by_team=dependencies_by_team)

# Save output
with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html generated.")

