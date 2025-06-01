import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the Jira CSV
df = pd.read_csv("docs/jira_data.csv")

# Filter to only Story tickets
df = df[df["Issue Type"] == "Story"]

# Keep only rows that have a blocking link
df = df[(df["Inward issue link (Blocks)"].notna()) | (df["Outward issue link (Blocks)"].notna())]

# Ensure missing fields are safe
df["Summary"] = df["Summary"] if "Summary" in df.columns else "N/A"
df["Summary"] = df["Summary"].fillna("N/A")
df["Components"] = df["Components"].fillna("Unassigned")

# Build structured output per team/component
team_data = {}

for _, row in df.iterrows():
    components = row["Components"].split(",") if pd.notna(row["Components"]) else ["Unassigned"]
    issue_key = row["Issue key"]
    summary = row["Summary"]
    blocked_by = row["Inward issue link (Blocks)"] if pd.notna(row["Inward issue link (Blocks)"]) else row["Outward issue link (Blocks)"]

    for component in components:
        team = component.strip()
        if team not in team_data:
            team_data[team] = []
        team_data[team].append({
            "key": issue_key,
            "summary": summary,
            "blocked_by": blocked_by
        })

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")

# Render to HTML
output = template.render(dependencies=team_data)

# Save HTML file
with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html generated successfully.")

