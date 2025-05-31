Bfunction loadDependencies(data) {
  const container = document.getElementById("dependency-summary");
  if (!container) return;

  const dependencyMap = {};

  data.forEach(row => {
    const issueKey = row["Key"];
    const summary = row["Summary"];
    const inward = row["Inward issue link (Blocks)"];
    const outward = row["Outward issue link (Blocks)"];

    if (inward || outward) {
      dependencyMap[issueKey] = {
        summary,
        blocks: [],
      };

      if (inward) {
        inward.split(',').forEach(dep => dependencyMap[issueKey].blocks.push(dep.trim()));
      }

      if (outward) {
        outward.split(',').forEach(dep => dependencyMap[issueKey].blocks.push(dep.trim()));
      }
    }
  });

  if (Object.keys(dependencyMap).length === 0) {
    container.innerHTML = "<p>No current blocking dependencies found in the dataset.</p>";
    return;
  }

  const table = document.createElement("table");
  table.className = "dependency-table";
  table.innerHTML = `
    <thead>
      <tr>
        <th>Ticket</th>
        <th>Summary</th>
        <th>Blocks / Blocked By</th>
      </tr>
    </thead>
    <tbody>
      ${Object.entries(dependencyMap).map(([key, info]) => `
        <tr>
          <td><strong>${key}</strong></td>
          <td>${info.summary}</td>
          <td>${info.blocks.join(", ")}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
  container.appendChild(table);
}

fetch("jira_data.csv")
  .then(response => response.text())
  .then(csv => {
    const data = Papa.parse(csv, { header: true }).data;
    renderSprintReadiness(data);
    renderBacklogHealth(data);
    renderProgramSummary(data);
    loadDependencies(data);
  });

