import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the data
df = pd.read_csv("docs/jira_data.csv")
df.columns = df.columns.str.strip()

# Define teams (from Components column)
teams = df["Components"].dropna().unique()

dependency_data = []

for team in teams:
    team_df = df[df["Components"] == team]

    # Clean up link fields and count dependencies
    inward = team_df["Inward issue link (Blocks)"].dropna().tolist()
    outward = team_df["Outward issue link (Blocks)"].dropna().tolist()

    total_dependencies = len(inward) + len(outward)

    dependency_data.append({
        "team": team,
        "inward_count": len(inward),
        "outward_count": len(outward),
        "total_dependencies": total_dependencies
    })

# Sort by team name
dependency_data = sorted(dependency_data, key=lambda x: x["team"])

# Setup Jinja2
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")

# Render HTML
output = template.render(dependency_data=dependency_data)

# Save to file
with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html generated.")

