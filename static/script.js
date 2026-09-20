// Load expenses when page opens
document.addEventListener("DOMContentLoaded", function () {
    loadExpenses();
});


// Get expenses from Flask backend
function loadExpenses() {

    fetch("/api/expenses")
        .then(response => response.json())
        .then(data => {

            console.log("Expenses received:", data);

            updateDashboard(data);
            displayExpenses(data);

        })
        .catch(error => {

            console.error("Error loading expenses:", error);

        });
}


// Update dashboard cards
function updateDashboard(expenses) {

    let total = 0;

    expenses.forEach(expense => {
        total += parseFloat(expense.amount);
    });

    let count = expenses.length;

    let average = count > 0 ? total / count : 0;

    document.getElementById("total-expenses").textContent =
        "₹" + total.toFixed(2);

    document.getElementById("transaction-count").textContent =
        count;

    document.getElementById("average-expense").textContent =
        "₹" + average.toFixed(2);
}


// Display expenses in history table
function displayExpenses(expenses) {

    const tableBody =
        document.getElementById("expense-table-body");

    tableBody.innerHTML = "";

    expenses.forEach(expense => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${expense.id}</td>
            <td>${expense.expense_name}</td>
            <td>₹${parseFloat(expense.amount).toFixed(2)}</td>
            <td>${expense.paid_by}</td>
            <td>${expense.participants}</td>
            <td>${expense.date}</td>
            <td>${expense.category}</td>
        `;

        tableBody.appendChild(row);

    });
}


// Add new expense
document.getElementById("expense-form").addEventListener("submit", function (event) {

    event.preventDefault();

    const expenseData = {

        expense_name:
            document.getElementById("expense_name").value,

        amount:
            document.getElementById("amount").value,

        paid_by:
            document.getElementById("paid_by").value,

        participants:
            document.getElementById("participants").value,

        date:
            document.getElementById("date").value,

        category:
            document.getElementById("category").value
    };


    fetch("/api/expenses", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(expenseData)

    })

    .then(response => response.json())

    .then(data => {

        console.log("Expense added:", data);

        document.getElementById("message").textContent =
            "Expense added successfully!";

        document.getElementById("expense-form").reset();

        // Reload dashboard and history
        loadExpenses();

    })

    .catch(error => {

        console.error("Error adding expense:", error);

        document.getElementById("message").textContent =
            "Error adding expense.";

    });

});