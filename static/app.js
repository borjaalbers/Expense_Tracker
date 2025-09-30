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
    const monthBadge = document.getElementById('budgetStatusMonth');
    const stateBadge = document.getElementById('budgetStatusState');
    const limitDisplay = document.getElementById('budgetLimitDisplay');
    const spentDisplay = document.getElementById('budgetSpent');
    const remainingDisplay = document.getElementById('budgetRemaining');
    const limitInput = document.getElementById('budgetLimit');

    if (!container) return;

    monthBadge.textContent = status.month || '';

    // State badge styling
    const state = status.status || 'no_budget';
    stateBadge.textContent = state;
    stateBadge.classList.remove('bg-info', 'bg-success', 'bg-warning', 'bg-danger', 'bg-secondary');
    if (state === 'ok') stateBadge.classList.add('bg-success');
    else if (state === 'warning') stateBadge.classList.add('bg-warning');
    else if (state === 'over') stateBadge.classList.add('bg-danger');
    else stateBadge.classList.add('bg-secondary');

    // Numbers
    const limit = status.limit;
    const spent = status.spent || 0.0;
    const remaining = status.remaining;

    limitDisplay.textContent = limit != null ? Number(limit).toFixed(2) : '—';
    spentDisplay.textContent = Number(spent).toFixed(2);
    remainingDisplay.textContent = remaining != null ? Number(remaining).toFixed(2) : '—';

    // Prefill limit input with current limit if any
    if (limitInput) {
        limitInput.value = limit != null ? Number(limit).toFixed(2) : '';
    }

    container.style.display = 'block';
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
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
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
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
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
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
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