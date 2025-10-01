// ============================================
// Constants
// ============================================
const BUDGET_WARNING_THRESHOLD = 0.9;    // 90% of budget
const BUDGET_DANGER_THRESHOLD = 1.10;    // 110% of average spending pace
const BUDGET_COLOR_GREEN = '#00c853';
const BUDGET_COLOR_YELLOW = '#ffc107';
const BUDGET_COLOR_RED = '#dc3545';

const CHART_COLORS = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
];

// ============================================
// API Helper
// ============================================
// Universal helper for API calls
async function api(path, method = "GET", body = null) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json",
        },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
    }
    return data;
}

// Auth UI logic (index page)
document.addEventListener("DOMContentLoaded", function () {
    // Chart.js dark theme defaults for readability
    if (window.Chart && Chart.defaults) {
        Chart.defaults.color = '#e0e0e0';
        Chart.defaults.borderColor = '#2c2c2c';
        Chart.defaults.plugins.legend.labels.color = '#e0e0e0';
        Chart.defaults.scales = Chart.defaults.scales || {};
    }
    const signinForm = document.getElementById("signinForm");
    if (signinForm) {
        signinForm.onsubmit = async (e) => {
            e.preventDefault();
            const username = document.getElementById("signinUsername").value;
            const password = document.getElementById("signinPassword").value;
            try {
                await api("/api/signin", "POST", { username, password });
                window.location.href = "/dashboard";
            } catch (err) {
                alert("Sign in failed: " + err.message);
            }
        };
    }

    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.onsubmit = async (e) => {
            e.preventDefault();
            const username = document.getElementById("signupUsername").value;
            const password = document.getElementById("signupPassword").value;
            try {
                await api("/api/signup", "POST", { username, password });
                window.location.href = "/dashboard";
            } catch (err) {
                alert("Sign up failed: " + err.message);
            }
        };
    }

    const signoutBtn = document.getElementById("signoutBtn");
    if (signoutBtn) {
        signoutBtn.onclick = async () => {
            try {
                await api("/api/signout", "POST");
                window.location.href = "/";
            } catch (err) {
                alert("Sign out failed: " + err.message);
            }
        };
    }

    // Dashboard logic
    if (window.location.pathname === "/dashboard") {
        initDashboard();
    }
});

// Chart instances
let categoryChart = null;
let monthlyChart = null;

// Dashboard logic
function initDashboard() {
    loadExpenses();
    loadSummary();
    loadMonthlyTotals();
    initBudgetUI();
    initCategoriesUI();
    initScopeControls();

    const expenseForm = document.getElementById("expenseForm");
    if (expenseForm) {
        expenseForm.onsubmit = addExpense;
    }

    // Set today's date as default
    const dateInput = document.getElementById("date");
    if (dateInput) {
        dateInput.value = new Date().toISOString().split("T")[0];
    }

    // Filter buttons
    document.getElementById("filterAll").onclick = () => loadExpenses("all");
    document.getElementById("filterToday").onclick = () => loadExpenses("today");
    document.getElementById("filterWeek").onclick = () => loadExpenses("week");
}

// ---------------- Scope (Month/Year) ----------------
let currentScope = { mode: 'month', month: null, year: null };

function initScopeControls() {
    const modeMonth = document.getElementById('scopeModeMonth');
    const modeYear = document.getElementById('scopeModeYear');
    const monthInput = document.getElementById('scopeMonth');
    const yearInput = document.getElementById('scopeYear');
    const monthWrap = document.getElementById('scopeMonthWrap');
    const yearWrap = document.getElementById('scopeYearWrap');
    const applyBtn = document.getElementById('applyScopeBtn');
    if (!modeMonth || !modeYear || !monthInput || !yearInput || !applyBtn) return;

    // Defaults to current month/year
    const now = new Date();
    const yyyy = now.getUTCFullYear();
    const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
    monthInput.value = `${yyyy}-${mm}`;
    yearInput.value = yyyy;
    currentScope = { mode: 'month', month: monthInput.value, year: yyyy };

    function updateModeDisplay() {
        const isMonth = modeMonth.checked;
        monthWrap.style.display = isMonth ? '' : 'none';
        yearWrap.style.display = isMonth ? 'none' : '';
    }

    modeMonth.onchange = updateModeDisplay;
    modeYear.onchange = updateModeDisplay;
    updateModeDisplay();

    applyBtn.onclick = async () => {
        const isMonth = modeMonth.checked;
        currentScope.mode = isMonth ? 'month' : 'year';
        currentScope.month = isMonth ? monthInput.value : null;
        currentScope.year = isMonth ? null : parseInt(yearInput.value, 10);

        // Recompute and refresh UI based on scope
        await refreshAllForScope();
    };
}

async function refreshAllForScope() {
    // Fetch all expenses, then filter on client based on scope
    try {
        const all = await api('/api/expenses');
        const { filtered, dateFrom, dateTo } = filterExpensesByScope(all, currentScope);
        displayExpenses(filtered);
        updateFilterButtons('all');

        // Recompute summary and monthly charts from filtered data
        const summary = computeSummaryByCategory(filtered);
        displaySummary(summary);
        drawCategoryChart(summary);

        const monthly = computeMonthlyTotals(filtered);
        displayMonthlyTotals(monthly);
        drawMonthlyChart(monthly);
        // Keep budget status in sync with current scope/month selection
        refreshBudgetUI();
    } catch (err) {
        console.error('Failed to refresh for scope:', err);
    }
}

function filterExpensesByScope(expenses, scope) {
    if (!expenses || expenses.length === 0) return { filtered: [], dateFrom: null, dateTo: null };
    if (scope.mode === 'month' && scope.month) {
        const prefix = scope.month; // YYYY-MM
        const filtered = expenses.filter(e => (e.date || '').startsWith(prefix));
        return { filtered, dateFrom: `${prefix}-01`, dateTo: `${prefix}-31` };
    } else if (scope.mode === 'year' && scope.year) {
        const y = String(scope.year);
        const filtered = expenses.filter(e => (e.date || '').startsWith(y + '-'));
        return { filtered, dateFrom: `${y}-01-01`, dateTo: `${y}-12-31` };
    }
    return { filtered: expenses, dateFrom: null, dateTo: null };
}

function computeSummaryByCategory(expenses) {
    const sums = {};
    for (const e of expenses) {
        const cat = e.category || 'Uncategorized';
        sums[cat] = (sums[cat] || 0) + (e.amount || 0);
    }
    return sums;
}

function computeMonthlyTotals(expenses) {
    const totals = {};
    for (const e of expenses) {
        const ym = (e.date || '').slice(0, 7); // YYYY-MM
        if (!ym) continue;
        totals[ym] = (totals[ym] || 0) + (e.amount || 0);
    }
    // Sorted
    return Object.fromEntries(Object.entries(totals).sort((a, b) => a[0].localeCompare(b[0])));
}

// ---------------- Categories UI ----------------
function initCategoriesUI() {
    const addBtn = document.getElementById('addCategoryBtn');
    const nameInput = document.getElementById('newCategoryName');
    const selectEl = document.getElementById('category');
    const listEl = document.getElementById('categoryList');
    if (!addBtn || !nameInput || !selectEl || !listEl) return;

    async function refreshCategories() {
        try {
            const cats = await api('/api/categories');
            // Populate dropdown
            const current = selectEl.value;
            selectEl.innerHTML = '<option value="">Select a category</option>' +
                cats.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
            // Keep current selection if still present
            if (current && cats.some(c => c.name === current)) {
                selectEl.value = current;
            }
            // Render as a clean list
            listEl.innerHTML = `
                <ul class="list-group list-group-flush">
                    ${cats.map(c => `
                        <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent text-light py-1">
                            <span class="small">${c.name}</span>
                            <button type="button" class="btn btn-sm btn-outline-danger" data-cat-id="${c.id}">
                                Remove
                            </button>
                        </li>
                    `).join('')}
                </ul>
            `;
            // Wire delete buttons
            listEl.querySelectorAll('button[data-cat-id]').forEach(btn => {
                btn.onclick = async () => {
                    const id = btn.getAttribute('data-cat-id');
                    try {
                        await api(`/api/categories/${id}`, 'DELETE');
                        await refreshCategories();
                    } catch (err) {
                        alert('Failed to delete category: ' + err.message);
                    }
                };
            });
        } catch (err) {
            console.error('Failed to load categories:', err);
        }
    }

    addBtn.onclick = async () => {
        const name = nameInput.value.trim();
        if (!name) return;
        try {
            await api('/api/categories', 'POST', { name });
            nameInput.value = '';
            await refreshCategories();
        } catch (err) {
            alert('Failed to add category: ' + err.message);
        }
    };

    // Initial load
    refreshCategories();
}

// ---------------- Budget UI ----------------
function initBudgetUI() {
    const monthInput = document.getElementById("budgetMonth");
    const limitInput = document.getElementById("budgetLimit");
    const form = document.getElementById("budgetForm");
    if (!monthInput || !limitInput || !form) {
        return; // Budget UI not on this page
    }

    // Default to current month
    const now = new Date();
    const yyyy = now.getUTCFullYear();
    const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
    const currentMonth = `${yyyy}-${mm}`;
    monthInput.value = currentMonth;

    // Load current month status
    loadBudgetStatus(currentMonth);

    // Change month -> reload status
    monthInput.onchange = () => {
        loadBudgetStatus(monthInput.value);
    };

    // Save budget
    form.onsubmit = async (e) => {
        e.preventDefault();
        const month = monthInput.value;
        const limitVal = parseFloat(limitInput.value);
        if (!month) {
            alert("Please choose a month");
            return;
        }
        if (!Number.isFinite(limitVal) || limitVal <= 0) {
            alert("Limit must be a number greater than 0");
            return;
        }
        try {
            await api('/api/budget', 'POST', { month, limit_amount: limitVal });
            await loadBudgetStatus(month);
            // Refresh monthly chart and totals since remaining depends on spending
            await loadMonthlyTotals();
        } catch (err) {
            alert('Failed to save budget: ' + err.message);
        }
    };
}

async function loadBudgetStatus(month) {
    try {
        const status = await api(`/api/budget?month=${encodeURIComponent(month)}`);
        displayBudgetStatus(status);
    } catch (err) {
        console.error('Failed to load budget:', err);
    }
}

function displayBudgetStatus(status) {
    const container = document.getElementById('budgetStatus');
    if (!container) return;

    updateBudgetBadges(status);
    updateBudgetNumbers(status);
    updateBudgetProgressBar(status);
    
    container.style.display = 'block';
}

// Helper: Update budget status badges
function updateBudgetBadges(status) {
    const monthBadge = document.getElementById('budgetStatusMonth');
    const stateBadge = document.getElementById('budgetStatusState');
    
    monthBadge.textContent = status.month || '';
    
    const state = status.status || 'no_budget';
    stateBadge.textContent = state;
    stateBadge.classList.remove('bg-info', 'bg-success', 'bg-warning', 'bg-danger', 'bg-secondary');
    if (state === 'ok') stateBadge.classList.add('bg-success');
    else if (state === 'warning') stateBadge.classList.add('bg-warning');
    else if (state === 'over') stateBadge.classList.add('bg-danger');
    else stateBadge.classList.add('bg-secondary');
}

// Helper: Update budget numbers display
function updateBudgetNumbers(status) {
    const limitDisplay = document.getElementById('budgetLimitDisplay');
    const spentDisplay = document.getElementById('budgetSpent');
    const remainingDisplay = document.getElementById('budgetRemaining');
    const limitInput = document.getElementById('budgetLimit');
    
    const limit = status.limit;
    const spent = status.spent || 0.0;
    const remaining = status.remaining;

    limitDisplay.textContent = limit != null ? Number(limit).toFixed(2) : '—';
    spentDisplay.textContent = Number(spent).toFixed(2);
    remainingDisplay.textContent = remaining != null ? Number(remaining).toFixed(2) : '—';

    if (limitInput) {
        limitInput.value = limit != null ? Number(limit).toFixed(2) : '';
    }
}

// Helper: Update budget progress bar with color
function updateBudgetProgressBar(status) {
    const progressBar = document.getElementById('budgetProgress');
    if (!progressBar) return;

    const limit = status.limit;
    const spent = status.spent || 0.0;
    
    // Calculate percentage
    let pct = 0;
    if (limit && limit > 0) {
        pct = Math.max(0, Math.min(100, (spent / limit) * 100));
    }
    progressBar.style.width = pct.toFixed(0) + '%';

    // Set color based on spending pace
    const color = calculateBudgetColor(status);
    progressBar.style.background = color;
}

// Helper: Calculate budget progress bar color based on spending pace
function calculateBudgetColor(status) {
    try {
        const limit = status.limit;
        const spent = status.spent || 0.0;
        const month = (status.month || '');
        
        const [y, m] = month.split('-').map(Number);
        const daysInMonth = new Date(y, m, 0).getDate();
        const today = new Date();
        const todayY = today.getUTCFullYear();
        const todayM = today.getUTCMonth() + 1;
        const todayD = today.getUTCDate();
        const isCurrentMonth = (y === todayY && m === todayM);
        const elapsedDays = isCurrentMonth ? Math.max(1, todayD) : daysInMonth;

        const avgAllowedPerDay = limit && limit > 0 ? limit / daysInMonth : 0;
        const avgSpentPerDaySoFar = elapsedDays > 0 ? spent / elapsedDays : 0;

        // Green if on track, yellow if slightly over, red if significantly over
        if (avgSpentPerDaySoFar > avgAllowedPerDay * BUDGET_DANGER_THRESHOLD) {
            return BUDGET_COLOR_RED;
        } else if (avgSpentPerDaySoFar > avgAllowedPerDay) {
            return BUDGET_COLOR_YELLOW;
        }
        return BUDGET_COLOR_GREEN;
    } catch (e) {
        return BUDGET_COLOR_GREEN; // Fallback
    }
}

// --- Budget helpers ---
function getDesiredBudgetMonth() {
    const monthInput = document.getElementById('budgetMonth');
    if (monthInput && monthInput.value) return monthInput.value;
    if (typeof currentScope !== 'undefined' && currentScope.mode === 'month' && currentScope.month) {
        return currentScope.month;
    }
    const now = new Date();
    const yyyy = now.getUTCFullYear();
    const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
    return `${yyyy}-${mm}`;
}

function refreshBudgetUI() {
    const month = getDesiredBudgetMonth();
    loadBudgetStatus(month);
}

async function addExpense(event) {
    event.preventDefault();
    const amount = parseFloat(document.getElementById("amount").value);
    const category = document.getElementById("category").value;
    const date = document.getElementById("date").value;
    const note = document.getElementById("note").value;

    // Validate amount
    if (amount <= 0) {
        alert("Amount must be greater than 0");
        return;
    }

    try {
        await api("/api/expenses", "POST", {
            amount,
            category,
            date,
            note,
        });
        clearAddForm();
        loadExpenses();
        loadSummary();
        loadMonthlyTotals();
        refreshBudgetUI();
    } catch (err) {
        alert("Failed to add expense: " + err.message);
    }
}

function clearAddForm() {
    document.getElementById("amount").value = "";
    document.getElementById("category").value = "";
    document.getElementById("date").value = new Date().toISOString().split("T")[0];
    document.getElementById("note").value = "";
}

// Edit expense function
async function editExpense(expenseId) {
    try {
        const expense = await api(`/api/expenses/${expenseId}`);
        
        // Populate form with expense data
        document.getElementById("amount").value = expense.amount;
        document.getElementById("category").value = expense.category;
        document.getElementById("date").value = expense.date;
        document.getElementById("note").value = expense.note;
        
        // Change form to edit mode
        const form = document.getElementById("expenseForm");
        const submitBtn = document.getElementById("addBtn");
        
        submitBtn.textContent = "Update Expense";
        submitBtn.onclick = async (e) => {
            e.preventDefault();
            await updateExpense(expenseId);
        };
        
        // Scroll to form
        form.scrollIntoView({ behavior: 'smooth' });
        
    } catch (err) {
        alert("Failed to load expense for editing: " + err.message);
    }
}

// Update expense function
async function updateExpense(expenseId) {
    const amount = parseFloat(document.getElementById("amount").value);
    const category = document.getElementById("category").value;
    const date = document.getElementById("date").value;
    const note = document.getElementById("note").value;

    // Validate amount
    if (amount <= 0) {
        alert("Amount must be greater than 0");
        return;
    }

    try {
        await api(`/api/expenses/${expenseId}`, "PUT", {
            amount,
            category,
            date,
            note,
        });
        
        // Reset form
        clearAddForm();
        const submitBtn = document.getElementById("addBtn");
        submitBtn.textContent = "Add Expense";
        submitBtn.onclick = addExpense;
        
        // Refresh data
        loadExpenses();
        loadSummary();
        loadMonthlyTotals();
        refreshBudgetUI();
        
    } catch (err) {
        alert("Failed to update expense: " + err.message);
    }
}

// Delete expense function
async function deleteExpense(expenseId) {
    if (!confirm("Are you sure you want to delete this expense?")) {
        return;
    }
    
    try {
        await api(`/api/expenses/${expenseId}`, "DELETE");
        loadExpenses();
        loadSummary();
        loadMonthlyTotals();
        refreshBudgetUI();
    } catch (err) {
        alert("Failed to delete expense: " + err.message);
    }
}

async function loadExpenses(filter = "all") {
    try {
        const expenses = await api("/api/expenses");
        let filtered = expenses;

        if (filter === "today") {
            const today = new Date().toISOString().split("T")[0];
            filtered = expenses.filter((exp) => exp.date === today);
        } else if (filter === "week") {
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            const weekAgoStr = weekAgo.toISOString().split("T")[0];
            filtered = expenses.filter((exp) => exp.date >= weekAgoStr);
        }

        displayExpenses(filtered);
        updateFilterButtons(filter);
    } catch (err) {
        console.error("Failed to load expenses:", err);
    }
}

function displayExpenses(expenses) {
    const container = document.getElementById("expensesList");
    if (expenses.length === 0) {
        container.innerHTML = "<p class='text-muted'>No expenses found.</p>";
        return;
    }

    container.innerHTML = expenses
        .map(
            (exp) => `
        <div class="expense-item border-bottom pb-2 mb-2">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <div class="expense-amount fw-bold">$${exp.amount.toFixed(2)}</div>
                    <div class="expense-category badge bg-secondary">${exp.category}</div>
                    ${exp.note ? `<div class="expense-note text-muted small mt-1">${exp.note}</div>` : ""}
                </div>
                <div class="text-end">
                    <div class="expense-date text-muted small">${exp.date}</div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editExpense(${exp.id})">Edit</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense(${exp.id})">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    `
        )
        .join("");
}

// Chart drawing functions
function drawCategoryChart(summary) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    if (Object.keys(summary).length === 0) {
        return;
    }
    
    const labels = Object.keys(summary);
    const data = Object.values(summary);
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: CHART_COLORS.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

function drawMonthlyChart(totals) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    if (Object.keys(totals).length === 0) {
        return;
    }
    
    // Sort months chronologically
    const sortedEntries = Object.entries(totals).sort((a, b) => a[0].localeCompare(b[0]));
    const labels = sortedEntries.map(([month, _]) => month);
    const data = sortedEntries.map(([_, total]) => total);
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Spending',
                data: data,
                backgroundColor: '#36A2EB',
                borderColor: '#36A2EB',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function updateFilterButtons(activeFilter) {
    document.getElementById("filterAll").classList.toggle("active", activeFilter === "all");
    document.getElementById("filterToday").classList.toggle("active", activeFilter === "today");
    document.getElementById("filterWeek").classList.toggle("active", activeFilter === "week");
}

async function loadSummary() {
    try {
        const summary = await api("/api/summary");
        displaySummary(summary);
        drawCategoryChart(summary);
    } catch (err) {
        console.error("Failed to load summary:", err);
    }
}

function displaySummary(summary) {
    const container = document.getElementById("categorySummary");
    if (Object.keys(summary).length === 0) {
        container.innerHTML = "<p class='text-muted'>No expenses found.</p>";
        return;
    }

    container.innerHTML = Object.entries(summary)
        .map(
            ([category, total]) => `
        <div class="summary-item">
            <span>${category}</span>
            <span>$${total.toFixed(2)}</span>
        </div>
    `
        )
        .join("");
}

async function loadMonthlyTotals() {
    try {
        const totals = await api("/api/monthly");
        displayMonthlyTotals(totals);
        drawMonthlyChart(totals);
    } catch (err) {
        console.error("Failed to load monthly totals:", err);
    }
}

function displayMonthlyTotals(totals) {
    const container = document.getElementById("monthlyTotals");
    if (Object.keys(totals).length === 0) {
        container.innerHTML = "<p class='text-muted'>No expenses found.</p>";
        return;
    }

    container.innerHTML = Object.entries(totals)
        .map(
            ([month, total]) => `
        <div class="monthly-item">
            <span>${month}</span>
            <span>$${total.toFixed(2)}</span>
        </div>
    `
        )
        .join("");
}