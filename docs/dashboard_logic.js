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

    const isFutureSprint = sprint && !sprint.toLowerCase().includes("active");
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

function renderProgramSummary(data, teams, readinessStatuses, backlogStatuses) {
  const readiness = countByTeamAndStatus(data, teams, readinessStatuses, (status, sprint, isFuture) => isFuture && status !== "Done" && status !== "Blocked" && status !== "Cancelled" && status !== "In Progress");
  const backlog = countByTeamAndStatus(data, teams, backlogStatuses, (status, sprint, isFuture) => (isFuture || !sprint) && status !== "Done" && status !== "Blocked" && status !== "Cancelled" && status !== "In Progress");

  const teamScores = teams.map(team => {
    const rTotal = readiness[team].total || 0;
    const bTotal = backlog[team].total || 0;
    const rPct = rTotal ? (readiness[team].matched / rTotal) : 0;
    const bPct = bTotal ? (backlog[team].matched / bTotal) : 0;
    const avg = Math.round(((rPct + bPct) / 2) * 100);
    return { team, avg };
  });

  const programAvg = Math.round(teamScores.reduce((sum, t) => sum + t.avg, 0) / teamScores.length);
  const programColor = getStoplightColor(programAvg);
  const overallImg = document.getElementById("overallStoplight");
  overallImg.src = `blinking_${programColor}.gif`;
  overallImg.alt = `Overall is ${programColor}`;

  const tableBody = document.getElementById("summaryTableBody");
  tableBody.innerHTML = "";

  teamScores.forEach(({ team, avg }) => {
    const row = document.createElement("tr");

    const stoplightImg = document.createElement("img");
    stoplightImg.src = `blinking_${getStoplightColor(avg)}.gif`;
    stoplightImg.alt = `${getStoplightColor(avg)} stoplight`;
    stoplightImg.width = 40;

    row.innerHTML = `
      <td>${team}</td>
      <td>${stoplightImg.outerHTML}</td>
      <td>${avg}%</td>
      <td>${getProgramInterpretation(avg)}</td>
    `;

    tableBody.appendChild(row);
  });
}

function getProgramInterpretation(score) {
  if (score >= 80) return "On track — teams appear ready to execute.";
  if (score >= 50) return "Caution — backlog or readiness gaps emerging.";
  return "At risk — major prep or backlog issues present.";
}

