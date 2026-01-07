let paymentMethods = [];

function fetchPaymentMethodsAndAddRow() {
  fetch("/products/purchase/payment-methods/")
    .then(res => res.json())
    .then(data => {
      paymentMethods = data.methods || [];
      addPaymentRow(); // ✅ only after methods loaded
    });
}


function addPaymentRow() {
  const tbody = document.querySelector("#paymentTable tbody");
  const row = document.createElement("tr");
  const options = paymentMethods.map(m => `<option value="${m.id}">${m.name}</option>`).join("");

  row.innerHTML = `
    <td><select name="payment_method[]" class="form-select">${options}</select></td>
    <td><input type="number" name="payment_amount[]" class="form-control" min="0" step="0.01" max="{{ p.due }}" placeholder="৳" required></td>
    <td><input type="text" name="payment_note[]" class="form-control"></td>
    <td><button type="button" class="btn btn-sm btn-danger" onclick="this.closest('tr').remove()">🗑️</button></td>
  `;
  tbody.appendChild(row);
}

function openPaymentModal(purchaseId) {
  fetch(`/products/purchase/${purchaseId}/summary/`)
    .then(res => res.json())
    .then(data => {
      const p = data.purchase;
      document.querySelector("#paymentForm [name='reference_id']").value = p.id;

      // 🔹 Header Info
      document.getElementById("paymentInvoice").textContent = p.invoice_no;
      document.getElementById("paymentDate").textContent = p.date;
      document.getElementById("paymentSupplier").textContent = `${p.supplier.name} (${p.supplier.company_name}) - ${p.supplier.mobile}`;
      document.getElementById("paymentReference").textContent = p.reference || "—";

      document.getElementById("paymentTotal").textContent = p.total;
      document.getElementById("paymentDiscount").textContent = p.total_discount;
      document.getElementById("paymentNetTotal").textContent = p.net_total;
      document.getElementById("paymentPaid").textContent = p.paid;
      document.getElementById("paymentDue").textContent = p.due;

      // 🔹 Item List
      const itemList = document.getElementById("paymentItemList");
      itemList.innerHTML = "";
      p.items.forEach(item => {
        itemList.innerHTML += `
          <tr>
            <td>${item.product}</td>
            <td>${item.qty}</td>
            <td>৳${item.subtotal}</td>
          </tr>
        `;
      });

      // 🔹 Payment Rows
      document.querySelector("#paymentTable tbody").innerHTML = "";
      fetchPaymentMethodsAndAddRow(); // ✅ safe call
      bootstrap.Modal.getOrCreateInstance(document.getElementById("paymentModal")).show();
    })
    .catch(() => showToast("❌ পারচেস তথ্য লোড হয়নি", "danger"));
}
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

    input.reportValidity(); // ✅ triggers browser to re-check
  });

  if (sum > due) {
    showToast(`⚠️ মোট পেমেন্ট ৳${sum.toFixed(2)} > ডিউ ৳${due.toFixed(2)}`, "danger");
    return false;
  }

  return true;
}

function updateRemainingDue() {
  const due = parseFloat(document.getElementById("paymentDue").textContent);
  const inputs = document.querySelectorAll("input[name='payment_amount[]']");
  let sum = 0;
  inputs.forEach(i => sum += parseFloat(i.value || 0));

  const remaining = due - sum;
  document.getElementById("remainingDue").textContent = remaining.toFixed(2);
}

document.addEventListener("input", function (e) {
  if (e.target.name === "payment_amount[]") {
    validatePaymentTotal(); // ✅ live check
  }
});
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("paymentForm").addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validatePaymentTotal()) return;

    const formData = new FormData(this);

    fetch("/products/purchase/payment/", {
      method: "POST",
      headers: {
        "X-CSRFToken": formData.get("csrfmiddlewaretoken")
      },
      body: formData
    })
      .then(res => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then(data => {
        if (data.success) {
          showToast("✅ পেমেন্ট সফলভাবে সংরক্ষিত হয়েছে", "success");

          // ✅ Hide modal
          bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();

          // ✅ Refresh after short delay
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast("❌ " + data.message, "danger");

          // ✅ Optional: Hide modal even on error
          bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();

          // ✅ Optional: Refresh anyway
          setTimeout(() => location.reload(), 1500);
        }
      })
      .catch(err => {
        console.error("Fetch error:", err);
        showToast("❌ নেটওয়ার্ক সমস্যা হয়েছে, অনুগ্রহ করে আবার চেষ্টা করুন", "danger");

        // ✅ Hide modal even on network error
        bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();

        // ✅ Optional: Refresh anyway
        setTimeout(() => location.reload(), 1500);
      });
  });
});

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
