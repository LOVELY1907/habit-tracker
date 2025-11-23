// static/dashboard.js
(async function () {

  // DOM Elements
  const monthYearEl = document.getElementById("monthYear");
  const prevBtn = document.getElementById("prevMonth");
  const nextBtn = document.getElementById("nextMonth");
  const todayBtn = document.getElementById("todayBtn");
  const calendarEl = document.getElementById("calendar");
  const habitListEl = document.getElementById("habitList");
  const notificationsEl = document.getElementById("notifications");
  const insightsEl = document.getElementById("insights");
  const predictionsEl = document.getElementById("predictions");

  const addForm = document.getElementById("addHabitForm");
  const habitNameInput = document.getElementById("habitName");

  // Charts
  let habitChart, monthlyChart, weeklyChart;
  let viewDate = new Date();

  // --------------------------
  // EVENT LISTENERS
  // --------------------------
  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = habitNameInput.value.trim();
    if (!name) return;

    await fetch("/api/habits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    habitNameInput.value = "";
    await loadMonth(viewDate);
  });

  prevBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() - 1);
    loadMonth(viewDate);
  });

  nextBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() + 1);
    loadMonth(viewDate);
  });

  todayBtn.addEventListener("click", () => {
    viewDate = new Date();
    loadMonth(viewDate);
  });

  // Initial load
  await loadMonth(viewDate);

  // --------------------------
  // LOAD MONTH + UI REFRESH
  // --------------------------
  async function loadMonth(d) {
    const y = d.getFullYear(),
      m = d.getMonth() + 1;

    monthYearEl.textContent = d.toLocaleString(undefined, {
      month: "long",
      year: "numeric",
    });

    const res = await fetch(`/api/month/${y}/${m}`);
    if (res.status === 401) {
      window.location = "/login";
      return;
    }

    const data = await res.json();

    renderHabits(data.habits);
    renderCalendar(data.habits, data.completions, y, m);

    await fetchStats(y, m);
    await loadNotifications();
    await loadPredictions();
  }

  // --------------------------
  // RENDER HABIT LIST
  // --------------------------
  function renderHabits(habits) {
    habitListEl.innerHTML = "";

    if (!habits.length) {
      habitListEl.innerHTML =
        '<div class="text-sm text-gray-500">No habits yet</div>';
      return;
    }

    habits.forEach((h) => {
      const li = document.createElement("li");
      li.className =
        "flex items-center justify-between bg-[#FBFBFD] p-2 rounded";
      li.innerHTML = `
        <div class="text-sm">${escapeHtml(h.name)}</div>
        <div class="flex gap-2">
          <button class="rename text-xs text-blue-600" data-id="${h.id}">Rename</button>
          <button class="delete text-xs text-red-600" data-id="${h.id}">Delete</button>
        </div>`;

      habitListEl.appendChild(li);
    });

    // Delete habit
    habitListEl
      .querySelectorAll(".delete")
      .forEach((b) =>
        b.addEventListener("click", async (e) => {
          if (!confirm("Delete habit?")) return;

          await fetch(`/api/habits/${e.target.dataset.id}`, {
            method: "DELETE",
          });

          await loadMonth(viewDate);
        })
      );

    // Rename habit
    habitListEl
      .querySelectorAll(".rename")
      .forEach((b) =>
        b.addEventListener("click", async (e) => {
          const id = e.target.dataset.id;
          const newName = prompt("New name:");
          if (!newName) return;

          await fetch(`/api/habits/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName }),
          });

          await loadMonth(viewDate);
        })
      );
  }

  // --------------------------
  // RENDER CALENDAR
  // --------------------------
  function renderCalendar(habits, completions, year, month) {
    calendarEl.innerHTML = "";

    // Weekday headers
    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].forEach((d) => {
      const hd = document.createElement("div");
      hd.className = "text-xs text-gray-500 text-center";
      hd.textContent = d;
      calendarEl.appendChild(hd);
    });

    const first = new Date(year, month - 1, 1);
    const firstIdx = (first.getDay() + 6) % 7;
    const daysInMonth = new Date(year, month, 0).getDate();

    // Blank cells
    for (let i = 0; i < firstIdx; i++) {
      const cell = document.createElement("div");
      cell.className = "day-cell bg-transparent border-transparent";
      calendarEl.appendChild(cell);
    }

    // Actual days
    for (let d = 1; d <= daysInMonth; d++) {
      const dt = new Date(year, month - 1, d);
      const key = dt.toISOString().slice(0, 10);

      const cell = document.createElement("div");
      cell.className = "day-cell flex flex-col";

      cell.innerHTML = `
        <div class="flex justify-between items-start mb-2">
          <div class="day-number">${d}</div>
          <div class="text-xs text-gray-400">${dt.toLocaleString(undefined, {
            weekday: "short",
          })}</div>
        </div>
        <div class="habit-checks overflow-auto" style="flex:1"></div>`;

      calendarEl.appendChild(cell);

      const checks = cell.querySelector(".habit-checks");

      if (!habits.length) {
        checks.innerHTML =
          '<div class="text-xs text-gray-400">Add habits</div>';
      } else {
        habits.forEach((h) => {
          const checked = (completions[key] || []).includes(h.id);
          const id = `chk_${h.id}_${key}`;

          const row = document.createElement("div");
          row.className = "flex items-center gap-2 text-xs mb-1";
          row.innerHTML = `
              <input type="checkbox" id="${id}" ${
            checked ? "checked" : ""
          }>
              <label for="${id}" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px">
                ${escapeHtml(h.name)}
              </label>`;

          checks.appendChild(row);

          row.querySelector("input").addEventListener("change", async () => {
            await fetch("/api/completions/toggle", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ habit_id: h.id, date: key }),
            });

            await loadMonth(viewDate);
          });
        });
      }
    }
  }

  // --------------------------
  // STATS + CHARTS
  // --------------------------
  async function fetchStats(y, m) {
    const res = await fetch(`/api/stats/${y}/${m}`);
    const data = await res.json();

    renderCharts(data);
    renderInsights(data);
  }

  function renderCharts(d) {
    const habitLabels = d.habits.map((h) => h.name);
    const habitCounts = d.habit_counts.map((h) => h.count);

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: 10 },
      plugins: { legend: { display: false } }
    };

    // Habit-wise chart
    const hctx = document.getElementById("habitChart").getContext("2d");
    if (habitChart) habitChart.destroy();
    habitChart = new Chart(hctx, {
      type: "bar",
      data: { labels: habitLabels, datasets: [{ data: habitCounts }] },
      options: chartOptions,
    });

    // Monthly trend
    const monthlyLabels = d.daily_totals.map((_, i) => i + 1);
    const mctx = document.getElementById("monthlyChart").getContext("2d");
    if (monthlyChart) monthlyChart.destroy();
    monthlyChart = new Chart(mctx, {
      type: "line",
      data: { labels: monthlyLabels, datasets: [{ data: d.daily_totals, tension: 0.3, fill: true }]},
      options: chartOptions,
    });

    // Weekly chart
    const wctx = document.getElementById("weeklyChart").getContext("2d");
    if (weeklyChart) weeklyChart.destroy();
    weeklyChart = new Chart(wctx, {
      type: "bar",
      data: { labels: d.weekly.map((_, i) => `W${i + 1}`), datasets: [{ data: d.weekly }]},
      options: chartOptions,
    });
  }

  // --------------------------
  // INSIGHTS
  // --------------------------
  function renderInsights(d) {
    let html = `<p><strong>Overall:</strong> ${d.overall_percent}% this month.</p>`;

    const sorted = d.habit_counts.sort((a, b) => b.count - a.count);
    if (sorted.length) {
      html += `<p><strong>Top habit:</strong> ${escapeHtml(sorted[0].name)} — ${
        sorted[0].count
      }</p>`;
      html += `<p><strong>Needs attention:</strong> ${escapeHtml(
        sorted[sorted.length - 1].name
      )} — ${sorted[sorted.length - 1].count}</p>`;
    }

    html += `<div class="mt-2"><strong>Recommendations</strong><ul class="list-disc pl-5">`;

    if (d.overall_percent < 40)
      html += `<li>Your consistency is low — try focusing on 2–3 key habits.</li>`;
    else if (d.overall_percent < 70)
      html += `<li>Doing well — try improving weekly by 5%.</li>`;
    else html += `<li>Excellent! Consider adding a new challenge.</li>`;

    const zeros = d.habit_counts.filter((h) => h.count === 0).map((h) => h.name);
    if (zeros.length) html += `<li>Habits not done at all: ${zeros.join(", ")}</li>`;

    html += `</ul></div>`;

    insightsEl.innerHTML = html;
  }

  // --------------------------
  // NOTIFICATIONS
  // --------------------------
  async function loadNotifications() {
    const res = await fetch("/api/notifications");
    const data = await res.json();

    notificationsEl.innerHTML = "";

    if (!data.length) {
      notificationsEl.innerHTML =
        '<div class="text-sm text-gray-500">No notifications</div>';
      return;
    }

    data.forEach((n) => {
      const li = document.createElement("li");
      li.className =
        "bg-[#FBFBFD] p-2 rounded flex justify-between items-start";

      li.innerHTML = `
        <div>
          <div class="text-sm">${escapeHtml(n.message)}</div>
          <div class="text-xs text-gray-400 mt-1">${new Date(
            n.created_at
          ).toLocaleString()}</div>
        </div>
        <div>
          ${
            n.read
              ? '<span class="text-xs text-green-600">Read</span>'
              : `<button class="mark-read text-xs text-blue-600" data-id="${n.id}">Mark read</button>`
          }
        </div>
      `;

      notificationsEl.appendChild(li);
    });

    document
      .querySelectorAll(".mark-read")
      .forEach((b) =>
        b.addEventListener("click", async (e) => {
          await fetch(`/api/notifications/${e.target.dataset.id}/read`, {
            method: "POST",
          });
          await loadNotifications();
        })
      );
  }

  // --------------------------
  // ML PREDICTIONS
  // --------------------------
  async function loadPredictions() {
    const res = await fetch("/api/predict/nextday");
    const data = await res.json();

    predictionsEl.innerHTML = "";

    if (!data.length) {
      predictionsEl.innerHTML =
        '<div class="text-sm text-gray-500">No predictions</div>';
      return;
    }

    data.forEach((p) => {
      const div = document.createElement("div");
      const prob =
        p.probability_next_day === null
          ? "—"
          : Math.round(p.probability_next_day * 100) + "%";

      div.className = "text-sm";
      div.innerHTML = `<strong>${escapeHtml(p.name)}</strong> — ${prob}`;
      predictionsEl.appendChild(div);
    });
  }

  // Escape HTML helper
  function escapeHtml(s) {
    if (!s) return "";
    return s.replace(/[&<>"']/g, (m) => {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[m];
    });
  }
})();
