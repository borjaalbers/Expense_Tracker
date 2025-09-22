// static/app.js
// Universal helper for API calls
async function api(path, method="GET", body=null) {
    const opts = { method, headers: { "Accept": "application/json" } };
    if (body) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const resp = await fetch(path, opts);
    const data = await resp.json().catch(()=> ({}));
    if (!resp.ok) throw { status: resp.status, data };
    return data;
  }
  
  // ---------- Auth UI logic (index page) ----------
  document.addEventListener("DOMContentLoaded", function() {
    // Sign in
    const signinBtn = document.getElementById("signinBtn");
    if (signinBtn) {
      signinBtn.onclick = async () => {
        const username = document.getElementById("signinUsername").value;
        const password = document.getElementById("signinPassword").value;
        try {
          await api("/api/signin", "POST", { username, password });
          window.location.href = "/dashboard";
        } catch (err) {
          alert("Sign in failed: " + (err.data?.error || err.status));
        }
      }
    }
  
    // Sign up
    const signupBtn = document.getElementById("signupBtn");
    if (signupBtn) {
      signupBtn.onclick = async () => {
        const username = document.getElementById("signupUsername").value;
        const password = document.getElementById("signupPassword").value;
        try {
          await api("/api/signup", "POST", { username, password });
          window.location.href = "/dashboard";
        } catch (err) {
          alert("Sign up failed: " + (err.data?.error || err.status));
        }
      }
    }
  
    // Sign out button (in layout)
    const signoutBtn = document.getElementById("signoutBtn");
    if (signoutBtn) {
      signoutBtn.onclick = async () => {
        try {
          await api("/api/signout", "POST");
        } finally {
          window.location.href = "/";
        }
      }
    }
  
    // Dashboard related UI
    if (window.location.pathname === "/dashboard") {
      initDashboard();
    }
  });
  
  // ---------- Dashboard logic ----------
  function initDashboard() {
    const addBtn = document.getElementById("addBtn");
    const refreshBtn = document.getElementById("refreshBtn");
  
    addBtn.onclick = addExpense;
    refreshBtn.onclick = loadExpenses;
  
    loadExpenses();
    loadStats();
  }
  
  async function addExpense() {
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value || "Uncategorized";
    const date = document.getElementById("date").value || null;
    const note = document.getElementById("note").value || "";
  
    try {
      const payload = { amount: parseFloat(amount), category, note };
      if (date) payload.date = date;
      await api("/api/expenses", "POST", payload);
      clearAddForm();
      loadExpenses();
      loadStats();
    } catch (err) {
      alert("Failed to add expense: " + (err.data?.error || err.status));
    }
  }
  
  function clearAddForm() {
    document.getElementById("amount").value = "";
    document.getElementById("category").value = "";
    document.getElementById("date").value = "";
    document.getElementById("note").value = "";
  }
  
  async function loadExpenses() {
    const tbody = document.querySelector("#expensesTable tbody");
    tbody.innerHTML = "";
    try {
      const items = await api("/api/expenses", "GET");
      if (!items.length) {
        tbody.innerHTML = "<tr><td colspan='6'>No expenses yet</td></tr>";
        return;
      }
      for (const it of items) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${it.id}</td>
          <td>${parseFloat(it.amount).toFixed(2)}</td>
          <td>${it.category}</td>
          <td>${it.date}</td>
          <td>${it.note || ""}</td>
          <td>
            <button data-id="${it.id}" class="deleteBtn small">Delete</button>
            <button data-id="${it.id}" class="editBtn small">Edit</button>
          </td>`;
        tbody.appendChild(tr);
      }
      attachRowButtons();
    } catch (err) {
      tbody.innerHTML = "<tr><td colspan='6'>Failed to load expenses</td></tr>";
    }
    loadStats();
  }
  
  function attachRowButtons() {
    document.querySelectorAll(".deleteBtn").forEach(btn => {
      btn.onclick = async (e) => {
        const id = e.target.dataset.id;
        if (!confirm("Delete expense ID " + id + "?")) return;
        try {
          await api(`/api/expenses/${id}`, "DELETE");
          loadExpenses();
          loadStats();
        } catch (err) {
          alert("Delete failed");
        }
      }
    });
    document.querySelectorAll(".editBtn").forEach(btn => {
      btn.onclick = async (e) => {
        const id = e.target.dataset.id;
        const row = e.target.closest("tr");
        const amount = row.children[1].textContent;
        const category = row.children[2].textContent;
        const date = row.children[3].textContent;
        const note = row.children[4].textContent;
        const newAmount = prompt("Amount:", amount);
        if (newAmount === null) return;
        const newCategory = prompt("Category:", category);
        if (newCategory === null) return;
        const newDate = prompt("Date (YYYY-MM-DD):", date);
        if (newDate === null) return;
        const newNote = prompt("Note:", note);
        if (newNote === null) return;
        try {
          await api(`/api/expenses/${id}`, "PUT", {
            amount: parseFloat(newAmount),
            category: newCategory,
            date: newDate,
            note: newNote
          });
          loadExpenses();
          loadStats();
        } catch (err) {
          alert("Update failed: " + (err.data?.error || err.status || ""));
        }
      };
    });
  }
  
  // ---------- Stats (Chart.js) ----------
  let categoryChart = null;
  let monthlyChart = null;
  
  async function loadStats() {
    try {
      const sums = await api("/api/summary", "GET");
      const months = await api("/api/monthly", "GET");
      drawCategoryChart(sums);
      drawMonthlyChart(months);
    } catch (err) {
      console.error("Failed to load stats", err);
    }
  }
  
  function drawCategoryChart(sums) {
    const ctx = document.getElementById("categoryChart");
    if (!ctx) return;
    const labels = Object.keys(sums);
    const data = labels.map(k => sums[k]);
    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(ctx, {
      type: 'pie',
      data: { labels, datasets: [{ data }] },
      options: { responsive: true }
    });
  }
  
  function drawMonthlyChart(months) {
    const ctx = document.getElementById("monthlyChart");
    if (!ctx) return;
    const labels = Object.keys(months);
    const data = labels.map(k => months[k]);
    if (monthlyChart) monthlyChart.destroy();
    monthlyChart = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Total', data }] },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  }
  