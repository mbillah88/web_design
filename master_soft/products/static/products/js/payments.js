let paymentMethods = [];
let paymentMethodsLoaded = false;

function preloadPaymentMethods(callback = null) {
  if (paymentMethodsLoaded && paymentMethods.length > 0) {
    if (typeof callback === "function") callback();
    return;
  }

  fetch("/products/purchase/payment-methods/")
    .then(res => res.ok ? res.json() : Promise.reject("Server error"))
    .then(data => {
      paymentMethods = data.methods || [];
      paymentMethodsLoaded = true;

      if (typeof callback === "function") callback();
    })
    .catch(err => {
      console.error("❌ Payment methods fetch failed:", err);
      showToast("❌ পেমেন্ট মাধ্যম লোড হয়নি", "danger");
    });
}
function fetchPaymentMethodsAndAddRow() {
  preloadPaymentMethods(() => {
    addPaymentRow(); // ✅ only after methods loaded
  });
}
function openPaymentModal(purchaseId) {
  console.log("➡️ Opening payment modal for ID:", purchaseId);

  preloadPaymentMethods(() => {
    console.log("✅ Payment methods loaded");

    fetch(`/products/purchase/${purchaseId}/summary/`)
      .then(res => res.json())
      .then(data => {
        console.log("✅ Purchase summary:", data);

        const p = data.purchase;

        document.querySelector("#paymentForm [name='object_id']").value = p.id;
        document.querySelector("#paymentForm [name='type']").value = "purchase";
        document.querySelector("#paymentForm [name='content_type_id']").value = p.content_type_id;

        document.getElementById("paymentInvoice").textContent = p.invoice_no;
        document.getElementById("paymentDate").textContent = p.date;
        document.getElementById("paymentSupplier").textContent = `${p.supplier.name} (${p.supplier.company_name}) - ${p.supplier.mobile}`;
        document.getElementById("paymentReference").textContent = p.reference || "—";
        document.getElementById("paymentTotal").textContent = p.total;
        document.getElementById("paymentDiscount").textContent = p.total_discount;
        document.getElementById("paymentNetTotal").textContent = p.net_total;
        document.getElementById("paymentPaid").textContent = p.paid;
        document.getElementById("paymentDue").textContent = p.due;
        document.getElementById("remainingDue").textContent = p.due;

        // 🔹 Item Summary
        renderItemSummary(p.items);
        console.log("🧾 Items:", p.items);

        // Payments
        const tbody = document.querySelector("#paymentTable tbody");
        tbody.innerHTML = "";
        if (Array.isArray(p.payments)) {
          p.payments.forEach(payment => {
            if (typeof renderEditablePaymentRow === "function") {
              renderEditablePaymentRow(payment);
            } else {
              console.warn("⚠️ renderEditablePaymentRow not defined, skipping...");
            }
          });
        }

        // নতুন লাইন যোগ করা
        if (typeof addPaymentRow === "function") {
          addPaymentRow();
        }

        if (typeof updateRemainingDue === "function") {
          updateRemainingDue();
        }

        // Modal Show
        const modalEl = document.getElementById("paymentModal");
        if (modalEl) {
          console.log("✅ Showing modal now...");
          bootstrap.Modal.getOrCreateInstance(modalEl).show();
        } else {
          console.error("❌ Modal element not found in DOM!");
        }
      })
      .catch(err => {
        console.error("❌ Fetch error:", err);
        showToast("❌ পেমেন্ট তথ্য লোড হয়নি", "danger");
      });
  });
}
function renderEditablePaymentRow(payment) {
  const tbody = document.querySelector("#paymentTable tbody");
  const row = document.createElement("tr");
  const paymentId = payment?.id || Date.now();
  row.setAttribute("data-payment-id", paymentId);

  // 🔍 Match method name from payment.method__name
  const methodName = payment?.method__name?.trim().toLowerCase();

  const options = paymentMethods.map(m => {
    const selected = (m.name.trim().toLowerCase() === methodName) ? "selected" : "";
    return `<option value="${m.id}" ${selected}>${m.name}</option>`;
  }).join("");

  const dateHtml = formatDateTime(payment.created_at || payment.date);

  row.innerHTML = `
    <td><select class="form-select form-select-sm" name="method_${paymentId}">${options}</select></td>
    <td><input type="number" name="amount_${paymentId}" class="form-control form-control-sm" value="${payment?.amount ?? 0}" min="0" step="0.01"></td>
    <td><input type="text" name="note_${paymentId}" class="form-control form-control-sm" value="${payment?.note || ""}"></td>
    <td>${dateHtml}</td>
    <td>
      <button type="button" class="btn btn-sm btn-success" onclick="updatePaymentRow(${paymentId})">💾</button>
      <button type="button" class="btn btn-sm btn-danger" onclick="confirmDelete(${paymentId})">🗑️</button>
    </td>
  `;
  tbody.appendChild(row);
}
function renderItemSummary(items) {
  const itemList = document.getElementById("paymentItemList");
  itemList.innerHTML = "";
  
  console.log("🧾 Item:", items);

  if (!Array.isArray(items) || items.length === 0) {
    itemList.innerHTML = `<tr><td colspan="6" class="text-center text-muted">কোনো আইটেম পাওয়া যায়নি</td></tr>`;
    return;
  }

  items.forEach(item => {
    const product = item.product || "—";
    const qty = item.qty ?? "—";
    const price = item.price != null ? parseFloat(item.price).toFixed(2) : "—";
    const discount = item.discount != null ? parseFloat(item.discount).toFixed(2) : "—";
    const subtotal = item.subtotal != null ? parseFloat(item.subtotal).toFixed(2) : "—";

    let serials = "—";
    if (Array.isArray(item.serials) && item.serials.length > 0) {
      serials = item.serials.map(s => s.trim()).join(", ");
    }

    itemList.innerHTML += `
      <tr>
        <td>${product}</td>
        <td>${qty}</td>
        <td>৳${price}</td>
        <td>৳${discount}</td>
        <td>৳${subtotal}</td>
        <td><span class="text-muted small">${serials}</span></td>
      </tr>
    `;
  });
}


function addPaymentRow(defaultMethodId = null, suggestedAmount = null) {
  const tbody = document.querySelector("#paymentTable tbody");
  const row = document.createElement("tr");

  const options = paymentMethods.map(m => {
    const selected = (m.id === defaultMethodId) ? "selected" : "";
    return `<option value="${m.id}" ${selected}>${m.name}</option>`;
  }).join("");

  row.innerHTML = `
    <td><select name="payment_method[]" class="form-select">${options}</select></td>
    <td><input type="number" name="payment_amount[]" class="form-control" 
               min="0" step="0.01" placeholder="৳" value="${suggestedAmount ?? ''}" required></td>
    <td><input type="text" name="payment_note[]" class="form-control" placeholder="নোট"></td>
    <td>
      <button type="button" class="btn btn-sm btn-danger" 
              onclick="this.closest('tr').remove(); updateRemainingDue();">🗑️</button>
    </td>
  `;

  tbody.appendChild(row);

  // ✅ Auto-focus on amount field
  setTimeout(() => {
    row.querySelector("input[name='payment_amount[]']").focus();
  }, 100);

  updateRemainingDue();
}

function updatePaymentRow(paymentId) {
  const row = document.querySelector(`[data-payment-id='${paymentId}']`);
  if (!row) return;

  const method = row.querySelector(`[name='method_${paymentId}']`)?.value;
  const amount = row.querySelector(`[name='amount_${paymentId}']`)?.value;
  const note = row.querySelector(`[name='note_${paymentId}']`)?.value;

  const formData = new FormData();
  formData.append("method", method);
  formData.append("amount", amount);
  formData.append("note", note);

  fetch(`/products/purchase/payment/${paymentId}/update/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast("✅ আপডেট সফল", "success");
        updateRemainingDue();
      } else {
        showToast("❌ " + data.message, "danger");
      }
    })
    .catch(err => {
      console.error("Update error:", err);
      showToast("❌ সার্ভার সমস্যা", "danger");
    });
}
function refreshPaymentRow(paymentId, updatedData) {
  const row = document.querySelector(`[data-payment-id='${paymentId}']`);
  if (!row) return;

  row.querySelector(`[name='amount_${paymentId}']`).value = updatedData.amount;
  row.querySelector(`[name='note_${paymentId}']`).value = updatedData.note;
  row.querySelector(`[name='method_${paymentId}']`).value = updatedData.method.id;

  const timeCell = row.querySelector("td:nth-child(4)");
  if (timeCell) {
    timeCell.innerHTML = `
      <small class="text-muted d-block">${updatedData.date || "—"}</small>
      <small class="text-muted">${updatedData.updated_at?.split("T")[1]?.slice(0, 8) || "—"}</small>
    `;
  }
}
let pendingDeleteId = null;
let deletedPaymentCache = {};

function getCSRF() {
  return document.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";
}

function confirmDelete(paymentId) {
  pendingDeleteId = paymentId;
  const modalEl = document.getElementById("deleteConfirmModal");
  if (!modalEl) {
    console.error("❌ Confirmation modal not found!");
    return;
  }
  bootstrap.Modal.getOrCreateInstance(modalEl).show();
}

document.addEventListener("DOMContentLoaded", () => {
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", function () {
      if (!pendingDeleteId) return;

      const row = document.querySelector(`[data-payment-id='${pendingDeleteId}']`);
      if (!row) return;

      deletedPaymentCache[pendingDeleteId] = row.outerHTML;

      fetch(`/products/purchase/payment/${pendingDeleteId}/delete/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRF() }
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            row.remove();
            showUndoToast(pendingDeleteId);
            updateRemainingDue();
          } else {
            showToast("❌ " + (data.message || "ডিলিট হয়নি"), "danger");
          }
        })
        .catch(err => {
          console.error("❌ Delete error:", err);
          showToast("❌ সার্ভার সমস্যা", "danger");
        })
        .finally(() => {
          pendingDeleteId = null;
          bootstrap.Modal.getInstance(document.getElementById("deleteConfirmModal")).hide();
        });
    });
  }
});

function showUndoToast(paymentId) {
  const toast = document.createElement("div");
  toast.className = "toast align-items-center text-bg-warning border-0 show";
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.zIndex = "1055";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        🗑️ পেমেন্ট ডিলিট হয়েছে। <button class="btn btn-sm btn-light" onclick="undoDelete(${paymentId})">Undo</button>
      </div>
      <button type="button" class="btn-close me-2 m-auto" onclick="this.parentElement.parentElement.remove();"></button>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 10000);
}

function undoDelete(paymentId) {
  const cachedHTML = deletedPaymentCache[paymentId];
  if (!cachedHTML) return;

  const tbody = document.querySelector("#paymentTable tbody");
  const temp = document.createElement("div");
  temp.innerHTML = cachedHTML;
  const restoredRow = temp.firstElementChild;

  tbody.appendChild(restoredRow);
  showToast("✅ পেমেন্ট পুনরুদ্ধার হয়েছে", "success");

  delete deletedPaymentCache[paymentId];
}

function updateRemainingDue() {
  const total = parseFloat(document.getElementById("paymentNetTotal")?.textContent || 0);
  const paidRows = document.querySelectorAll("#paymentTable tbody tr");
  let totalPaid = 0;

  paidRows.forEach(row => {
    const amt = parseFloat(row.querySelector("input[name^='amount_']")?.value || 0);
    totalPaid += amt;
  });

  const due = total - totalPaid;
  document.getElementById("remainingDue").textContent = due.toFixed(2);
}

function editPayment(paymentId) {
  openPaymentModal(paymentId); // ✅ reuse modal logic
}
function updatePaymentRow(paymentId) {
  const row = document.querySelector(`[data-payment-id='${paymentId}']`);
  if (!row) return;

  const method = row.querySelector(`[name='method_${paymentId}']`)?.value;
  const amount = row.querySelector(`[name='amount_${paymentId}']`)?.value;
  const note = row.querySelector(`[name='note_${paymentId}']`)?.value;

  const formData = new FormData();
  formData.append("method", method);
  formData.append("amount", amount);
  formData.append("note", note);

  fetch(`/products/purchase/payment/${paymentId}/update/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast("✅ আপডেট সফল", "success");
        updateRemainingDue();
      } else {
        showToast("❌ " + data.message, "danger");
      }
    })
    .catch(err => {
      console.error("Update error:", err);
      showToast("❌ সার্ভার সমস্যা", "danger");
    });
}

function submitNewPayments(purchaseId) {
  const rows = document.querySelectorAll("#paymentTable tbody tr:not([data-payment-id])");
  if (rows.length === 0) {
    showToast("❌ কোনো নতুন পেমেন্ট নেই", "warning");
    return;
  }

  const formData = new FormData();
  formData.append("purchase_id", purchaseId);

  rows.forEach(row => {
    const method = row.querySelector("select[name='payment_method[]']")?.value;
    const amount = row.querySelector("input[name='payment_amount[]']")?.value;
    const note = row.querySelector("input[name='payment_note[]']")?.value;

    if (!method || parseFloat(amount) <= 0) return;

    formData.append("methods[]", method);
    formData.append("amounts[]", amount);
    formData.append("notes[]", note);
  });

  fetch(`/products/purchase/payment/bulk-create/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast("✅ নতুন পেমেন্ট যোগ হয়েছে", "success");
        refreshPaymentList(); // re-render table
      } else {
        showToast("❌ " + data.message, "danger");
      }
    })
    .catch(err => {
      console.error("Bulk create error:", err);
      showToast("❌ সার্ভার সমস্যা", "danger");
    });
}
function getSuggestedDueAmount() {
  const dueText = document.getElementById("remainingDue")?.textContent || "0";
  const due = parseFloat(dueText.replace(/[^\d.]/g, "")) || 0;
  return due > 0 ? due.toFixed(2) : "";
}
document.addEventListener("keydown", function (e) {
  if (e.key === "+") {
    e.preventDefault();
    addPaymentRow(paymentMethods[0].id, getSuggestedDueAmount());
  }
});

function validatePaymentTotal() {
  const due = parseFloat(document.getElementById("paymentDue").textContent);
  const inputs = document.querySelectorAll("input[name='payment_amount[]']");
  let sum = 0;

  inputs.forEach(input => {
    const val = parseFloat(input.value || 0);
    sum += val;

    if (val > due) {
      input.classList.add("is-invalid");
      input.setCustomValidity("পেমেন্ট ডিউয়ের চেয়ে বেশি!");
    } else {
      input.classList.remove("is-invalid");
      input.setCustomValidity("");
    }

    input.reportValidity();
  });

  updateRemainingDue();

  if (sum > due) {
    showToast(`⚠️ মোট পেমেন্ট ৳${sum.toFixed(2)} > ডিউ ৳${due.toFixed(2)}`, "danger");
    return false;
  }

  return true;
}
document.addEventListener("input", function (e) {
  if (e.target.name === "payment_amount[]") {
    validatePaymentTotal(); // ✅ live check
    updateRemainingDue();
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("paymentForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    if (!validatePaymentTotal()) return;

    const formData = new FormData(form);
    const paymentId = formData.get("payment_id");

    const url = paymentId
      ? `/products/purchase/payment/${paymentId}/update/`
      : `/products/purchase/payment/`;

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": formData.get("csrfmiddlewaretoken")
      },
      body: formData
    })
      .then(async res => {
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.message || "Server error");
        return data;
      })
      .then(data => {
        showToast(data.message || "✅ সফলভাবে সংরক্ষিত হয়েছে", "success");
        bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();
        setTimeout(() => location.reload(), 1000);
      })
      .catch(err => {
        console.error("Fetch error:", err);
        showToast("❌ " + err.message, "danger");
        bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();
        setTimeout(() => location.reload(), 1500);
      });
  });
});

function formatDateTime(iso) {
  const d = new Date(iso);
  const date = d.toLocaleDateString("bn-BD", { year: "numeric", month: "short", day: "numeric" });
  const time = d.toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  return `${date}<br><small class="text-muted">${time}</small>`;
}

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-bg-${type} border-0 show`;
  toast.role = "alert";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}
