import pandas as pd
import json

# Load CSV
df = pd.read_csv("../jira_data.csv")

# Rename columns for consistency
df = df.rename(columns={
    "Issue key": "Key",
    "Summary": "Summary",
    "Components": "Component",
    "Status": "Status",
    "Sprint": "Sprint",
    "Inward issue link (Blocks)": "Blocks",
    "Outward issue link (Blocks)": "BlockedBy"
})

# Drop rows without a valid Component or Status
df = df.dropna(subset=["Component", "Status"])

# Save clean JSON for dashboard use
output_path = "../docs/render_data.json"
df.to_json(output_path, orient="records", indent=2)

print(f"✅ Rendered {len(df)} tickets to: {output_path}")

