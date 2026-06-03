/**
 * Utilitaires et fonctions principales de l'application
 */

// API call helper
function apiCall(url, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(url, options)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .catch((error) => {
      console.error("Erreur API:", error);
      showAlert("Erreur", "Une erreur s'est produite", "danger");
      throw error;
    });
}

// Notification toast
function showAlert(title, message, type = "info") {
  const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <strong>${title}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

  const container = document.querySelector(".container-fluid");
  if (container) {
    const alertEl = document.createElement("div");
    alertEl.innerHTML = alertHtml;
    container.insertBefore(
      alertEl.firstElementChild,
      container.firstElementChild,
    );

    // Auto-dismiss après 5 secondes
    setTimeout(() => {
      const alert = container.querySelector(".alert");
      if (alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }
    }, 5000);
  }
}

// Confirmation dialog
function confirmAction(message) {
  return confirm(message);
}

// Format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XOF",
  }).format(amount);
}

// Format date
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

// Format datetime
function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Truncate text
function truncate(text, length = 50) {
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize tooltips (Bootstrap)
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(
    (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
  );
}

// Initialize popovers (Bootstrap)
function initPopovers() {
  const popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]'),
  );
  popoverTriggerList.map(
    (popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl),
  );
}

// Validate email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Validate phone number (format simple)
function validatePhone(phone) {
  const re = /^[\d\s\-\+\(\)]+$/;
  return re.test(phone) && phone.replace(/\D/g, "").length >= 7;
}

// Clear form
function clearForm(formId) {
  const form = document.getElementById(formId);
  if (form) {
    form.reset();
  }
}

// Set form values
function setFormValues(formId, data) {
  const form = document.getElementById(formId);
  if (form) {
    Object.keys(data).forEach((key) => {
      const input = form.elements[key];
      if (input) {
        if (input.type === "checkbox" || input.type === "radio") {
          input.checked = data[key];
        } else {
          input.value = data[key];
        }
      }
    });
  }
}

// Get form data as object
function getFormData(formId) {
  const form = document.getElementById(formId);
  if (!form) return {};

  const formData = new FormData(form);
  const data = {};

  formData.forEach((value, key) => {
    if (data.hasOwnProperty(key)) {
      if (Array.isArray(data[key])) {
        data[key].push(value);
      } else {
        data[key] = [data[key], value];
      }
    } else {
      data[key] = value;
    }
  });

  return data;
}

// Disable button during action
function disableButton(buttonEl, originalText = null) {
  buttonEl.disabled = true;
  if (originalText) {
    buttonEl.dataset.originalText = originalText;
  }
  buttonEl.innerHTML =
    '<span class="spinner-border spinner-border-sm me-2"></span>Chargement...';
}

// Enable button after action
function enableButton(buttonEl) {
  buttonEl.disabled = false;
  buttonEl.innerHTML = buttonEl.dataset.originalText || "Valider";
}

// Print document
function printDocument(elementId = null, title = "Document") {
  const printWindow = window.open("", "", "height=600,width=800");
  const content = elementId
    ? document.getElementById(elementId).innerHTML
    : document.body.innerHTML;

  printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>${title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                @media print {
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
            ${content}
            <script>
                window.print();
                window.close();
            </script>
        </body>
        </html>
    `);
  printWindow.document.close();
}

// Export table to CSV
function exportTableToCSV(tableId, filename = "export.csv") {
  const table = document.getElementById(tableId);
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll("tr");

  rows.forEach((row) => {
    let csvRow = [];
    const cells = row.querySelectorAll("td, th");

    cells.forEach((cell) => {
      csvRow.push(`"${cell.textContent.trim()}"`);
    });

    csv.push(csvRow.join(","));
  });

  const csvContent = csv.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
}

// Initialize on document ready
document.addEventListener("DOMContentLoaded", () => {
  initTooltips();
  initPopovers();
});

// Log helper for debugging
function log(...args) {
  if (process.env.NODE_ENV !== "production") {
    console.log("[APP]", ...args);
  }
}
