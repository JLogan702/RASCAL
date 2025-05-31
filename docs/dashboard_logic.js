async function loadDashboard(view) {
  const response = await fetch("jira_data.csv");
  const text = await response.text();
  const data = parseCSV(text);

  const teams = ["Engineering - Product", "Engineering - Platform", "Engineering - AI Ops", "Design", "Data Science"];
  const readinessStatuses = ["Ready for Development", "To Do"];
  const backlogStatuses = ["New", "Grooming"];

  if (view === "index") {
    renderProgramSummary(data, teams, readinessStatuses, backlogStatuses);
  } else if (view === "sprint_readiness") {
    renderSprintReadiness(data, teams, readinessStatuses);
  } else if (view === "backlog_health") {
    renderBacklogHealth(data, teams, backlogStatuses);
  } else if (view === "dependencies") {
    renderDependencies(data);
  }

  document.getElementById("lastUpdated").innerText = new Date().toLocaleString();
}

function parseCSV(csv) {
  const [headerLine, ...lines] = csv.trim().split("\n");
  const headers = headerLine.split(",");
  return lines.map(line => {
    const values = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
    const entry = {};
    headers.forEach((h, i) => entry[h.trim()] = (values[i] || "").trim().replace(/^"|"$/g, ""));
    return entry;
  });
}

function countByTeamAndStatus(data, teams, statuses, filterFn) {
  const result = {};
  teams.forEach(team => {
    result[team] = { total: 0, matched: 0, statusCounts: {} };
    statuses.forEach(status => result[team].statusCounts[status] = 0);
  });

  data.forEach(issue => {
    const team = issue["Components"];
    const status = issue["Status"];
    const sprint = issue["Sprint"];
    if (!teams.includes(team)) return;

    const isFutureSprint = sprint && sprint.trim().length > 0;
    const include = filterFn(status, sprint, isFutureSprint);

    if (include) {
      result[team].total++;
      if (statuses.includes(status)) {
        result[team].matched++;
        result[team].statusCounts[status]++;
      }
    }
  });

  return result;
}

function getStoplightColor(percent) {
  if (percent >= 80) return "green";
  if (percent >= 50) return "yellow";
  return "red";
}

function renderSprintReadiness(data, teams, statuses) {
  const container = document.getElementById("readinessContainer");
  const result = countByTeamAndStatus(data, teams, statuses, (status, sprint, isFuture) =>
    isFuture && !["Done", "Blocked", "Cancelled", "In Progress"].includes(status)
  );

  container.innerHTML = "";
  Object.entries(result).forEach(([team, metrics]) => {
    const percent = metrics.total ? Math.round((metrics.matched / metrics.total) * 100) : 0;
    const color = getStoplightColor(percent);

    const div = document.createElement("div");
    div.className = "team-box";
    div.innerHTML = `
      <h3>${team}</h3>
      <img src="blinking_${color}.gif" alt="${color}" />
      <p>Readiness: ${percent}%</p>
      <ul>${Object.entries(metrics.statusCounts).map(([s, c]) => `<li>${s}: ${c}</li>`).join("")}</ul>
      <p>This reflects tickets in future sprints in “To Do” or “Ready for Development”.</p>
    `;
    container.appendChild(div);
  });
}

function renderBacklogHealth(data, teams, statuses) {
  const container = document.getElementById("backlogContainer");
  const result = countByTeamAndStatus(data, teams, statuses, (status, sprint, isFuture) =>
    (!sprint || sprint.trim() === "") && !["Done", "Blocked", "Cancelled", "In Progress"].includes(status)
  );

  container.innerHTML = "";
  Object.entries(result).forEach(([team, metrics]) => {
    const percent = metrics.total ? Math.round((metrics.matched / metrics.total) * 100) : 0;
    const color = getStoplightColor(percent);

    const div = document.createElement("div");
    div.className = "team-box";
    div.innerHTML = `
      <h3>${team}</h3>
      <img src="blinking_${color}.gif" alt="${color}" />
      <p>Backlog Health: ${percent}%</p>
      <ul>${Object.entries(metrics.statusCounts).map(([s, c]) => `<li>${s}: ${c}</li>`).join("")}</ul>
      <p>This reflects backlog story tickets in “New” or “Grooming”.</p>
    `;
    container.appendChild(div);
  });
}

function renderProgramSummary(data, teams, readinessStatuses, backlogStatuses) {
  const readiness = countByTeamAndStatus(data, teams, readinessStatuses, (status, sprint, isFuture) =>
    isFuture && !["Done", "Blocked", "Cancelled", "In Progress"].includes(status)
  );

  const backlog = countByTeamAndStatus(data, teams, backlogStatuses, (status, sprint, isFuture) =>
    (!sprint || sprint.trim() === "") && !["Done", "Blocked", "Cancelled", "In Progress"].includes(status)
  );

  const teamScores = teams.map(team => {
    const rTotal = readiness[team].total || 0;
    const bTotal = backlog[team].total || 0;
    const rPct = rTotal ? (readiness[team].matched / rTotal) : 0;
    const bPct = bTotal ? (backlog[team].matched / bTotal) : 0;
    const avg = Math.round(((rPct + bPct) / 2) * 100);
    return { team, avg };
  });

  const programAvg = Math.round(teamScores.reduce((sum, t) => sum + t.avg, 0) / teamScores.length);
  const color = getStoplightColor(programAvg);
  const img = document.getElementById("overallStoplight");
  if (img) {
    img.src = `blinking_${color}.gif`;
    img.alt = `Program status is ${color}`;
  }

  const tableBody = document.getElementById("summaryTableBody");
  if (tableBody) {
    tableBody.innerHTML = "";
    teamScores.forEach(({ team, avg }) => {
      const row = document.createElement("tr");
      const stoplight = document.createElement("img");
      stoplight.src = `blinking_${getStoplightColor(avg)}.gif`;
      stoplight.width = 40;
      stoplight.alt = `${getStoplightColor(avg)} stoplight`;
      row.innerHTML = `
        <td>${team}</td>
        <td>${stoplight.outerHTML}</td>
        <td>${avg}%</td>
        <td>${getProgramInterpretation(avg)}</td>
      `;
      tableBody.appendChild(row);
    });
  }
}

function getProgramInterpretation(score) {
  if (score >= 80) return "On track — teams appear ready to execute.";
  if (score >= 50) return "Caution — backlog or readiness gaps emerging.";
  return "At risk — major prep or backlog issues present.";
}

function renderDependencies(data) {
  const container = document.getElementById("dependencyTableContainer");
  const filtered = data.filter(row => row["Inward issue link (Blocks)"] || row["Outward issue link (Blocks)"]);

  const table = document.createElement("table");
  table.innerHTML = `
    <thead>
      <tr><th>Ticket</th><th>Summary</th><th>Blocks</th><th>Is Blocked By</th><th>Component</th><th>Status</th></tr>
    </thead>
    <tbody>
      ${filtered.map(row => `
        <tr>
          <td>${row["Issue key"]}</td>
          <td>${row["Summary"]}</td>
          <td>${row["Outward issue link (Blocks)"]}</td>
          <td>${row["Inward issue link (Blocks)"]}</td>
          <td>${row["Components"]}</td>
          <td>${row["Status"]}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
  container.appendChild(table);
}

