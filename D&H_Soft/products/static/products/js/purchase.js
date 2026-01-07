let itemIndex = 1;
let serialMap = {};
let currentProductId = null;

function getCSRF() {
  const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (!tokenInput) {
    console.warn("⚠️ CSRF token not found");
    return "";
  }
  return tokenInput.value;
}

// ✅ Open Purchase Modal
function openPurchaseModal(purchaseId = null) {
  const form = document.getElementById("purchaseForm");
  const modal = document.getElementById("purchaseModal");
  const tbody = document.querySelector("#itemTable tbody");

  if (!form || !modal || !tbody) {
    showToast("❌ ফর্ম বা মোডাল পাওয়া যায়নি", "danger");
    return;
  }

  form.reset();
  tbody.innerHTML = "";
  serialMap = {};
  itemIndex = 1;

  if (purchaseId) {
  fetch(`/products/purchase/${purchaseId}/edit/`)
    .then(res => res.ok ? res.json() : Promise.reject("Server error"))
    .then(data => {
      const p = data.purchase;
      serialMap = p.serials || {};

      const fieldMap = {
        purchaseId: p.id,
        invoiceNo: p.invoice_no || "",
        purchaseDate: p.date || "",
        reference: p.reference || "",
        discountValue: p.total_discount || "0",
        discountType: p.discount_type || "amount",
        grandTotal: p.total || "0",
        subtotal: p.subtotal || "0"
        // ❌ supplierSelect বাদ দাও এখানে, কারণ Select2 AJAX dropdown
      };

      for (const [id, value] of Object.entries(fieldMap)) {
        const el = document.getElementById(id);
        if (el) el.value = value;
      }

      // ✅ Supplier pre-select for Select2 AJAX dropdown
      setSupplierInEdit(p.supplier_id);

      document.getElementById("itemCount").textContent = p.items.length;
      // ✅ Render item rows
      if (Array.isArray(p.items)) {
        p.items.forEach(item => renderItemRow(item));
      }

      updateItemCount();
      calculateTotals();

      document.getElementById("purchaseModalTitle").textContent = "✏️ পারচেস এডিট করুন";
      document.getElementById("savePurchaseBtn").textContent = "💾 আপডেট করুন";
      bootstrap.Modal.getOrCreateInstance(modal).show();
    })
    .catch(err => {
      console.error("❌ Error loading purchase:", err);
      showToast("❌ পারচেস তথ্য লোড হয়নি", "danger");
    });
} else {
    document.getElementById("purchaseId").value = "";
    document.getElementById("purchaseModalTitle").textContent = "➕ নতুন পারচেস যোগ করুন";
    document.getElementById("savePurchaseBtn").textContent = "💾 সেভ করুন";
    updateItemCount();
    calculateTotals();
    bootstrap.Modal.getOrCreateInstance(modal).show();
  }
}

function addItemRow(item) {
  const tbody = document.querySelector("#itemTable tbody");
  if (!tbody) return;

  const pid = item.product_id;
  const row = document.createElement("tr");
  row.id = `item-row-${pid}`;

  // 🔹 Warranty badge with tooltip
  const warrantyHTML = `
    <span class="badge bg-info text-dark" title="ওয়ারেন্টি">
      ${item.warranty || "—"}
    </span>
  `;

  // 🔹 Serial badge if applicable
  const serialBadge = item.is_serialized
    ? `<span class="badge bg-info">${serialMap?.[pid]?.length || 0} সিরিয়াল</span>`
    : "";

  // 🔹 Subtotal fallback
  const subtotal = item.subtotal || (item.qty * item.price - item.discount).toFixed(2);

  row.innerHTML = `
    <td>${itemIndex++}</td>
    <td>${item.code}</td>
    <td>${item.name}</td>
    <td>${warrantyHTML}</td>
    <td>
      <input type="number" class="form-control form-control-sm"
             name="qty_${pid}" id="qty_${pid}"
             value="${item.qty}" ${item.is_serialized ? "readonly" : ""}>
    </td>
    <td>
      <input type="number" class="form-control form-control-sm"
             name="price_${pid}" id="price_${pid}"
             value="${item.price}">
    </td>
    <td>
      <input type="number" class="form-control form-control-sm"
             name="discount_${pid}" id="discount_${pid}"
             value="${item.discount}">
    </td>
    <td>
      <input type="number" class="form-control form-control-sm"
             name="subtotal_${pid}" id="subtotal_${pid}"
             value="${subtotal}" readonly>
    </td>
    <td>${serialBadge}</td>
    <td>
      <button type="button" class="btn btn-sm btn-danger" onclick="removeItemRow('${pid}')">🗑️</button>
    </td>
  `;

  tbody.appendChild(row);
}
function renderItemRow(item) {
  const tbody = document.querySelector("#itemTable tbody");
  if (!tbody) return;

  const pid = item.product_id;
  const row = document.createElement("tr");
  row.id = `row-${pid}`;
  row.className = "text-center";

  const warrantyText = item.warranty || "—";
  const total = item.subtotal || (item.qty * item.price - item.discount).toFixed(2);

  let qtyHTML = "";
  if (item.is_serialized) {
    const serialCount = serialMap?.[pid]?.length || 0;
    qtyHTML = `
      <button type="button" class="btn btn-sm btn-outline-primary" onclick="openSerialModal(${pid})" title="Assign serials">🔢 Serial</button>
      <span class="badge bg-info ms-2" id="qty-${pid}">${serialCount}</span>
    `;
  } else {
    qtyHTML = `
      <input type="number" name="qty_${pid}" value="${item.qty}" min="1"
             class="form-control form-control-sm text-end qty-input">
    `;
  }

  row.innerHTML = `
    <td>${itemIndex++}</td>
    <td>${item.code}</td>
    <td>${item.name}</td>
    <td>${warrantyText}</td>
    <td>${qtyHTML}</td>
    <td>
      <input type="number" name="price_${pid}" value="${item.price}"
             class="form-control form-control-sm text-end price-input">
    </td>
    <td>
      <input type="number" name="discount_${pid}" value="${item.discount}"
             class="form-control form-control-sm text-end discount-input">
    </td>
    <td><span class="item-total fw-bold">৳${parseFloat(total).toFixed(2)}</span></td>
    <td>
      <button type="button" class="btn btn-sm btn-danger" onclick="removeItemRow(${pid})">🗑️</button>
    </td>
  `;

  tbody.appendChild(row);
}

function deletePurchase(purchaseId) {
  if (!confirm("❌ আপনি কি নিশ্চিতভাবে এই পারচেস ডিলিট করতে চান?")) return;

  fetch(`/products/purchase/${purchaseId}/delete/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken()
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast("🗑️ পারচেস ডিলিট হয়েছে", "success");
        document.getElementById(`purchase-row-${purchaseId}`)?.remove();
      } else {
        showToast("❌ " + data.message, "danger");
      }
    })
    .catch(() => showToast("❌ নেটওয়ার্ক সমস্যা", "danger"));
}

// ✅ Open Supplier Modal
function openSupplierModal() {
  const modalEl = document.getElementById("supplierModal");
  if (!modalEl) return showToast("❌ Supplier modal not found", "danger");

  try {
    bootstrap.Modal.getOrCreateInstance(modalEl).show();
  } catch (err) {
    console.error("Modal error:", err);
    showToast("❌ Modal open failed", "danger");
  }
}

// ✅ Submit Supplier Form
document.getElementById("supplierForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const form = this;
  const formData = new FormData(form);

  fetch("/products/supplier/create/", {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message);
        bootstrap.Modal.getInstance(document.getElementById("supplierModal")).hide();
        form.reset();

        const select = document.getElementById("supplierSelect");
        if (select) {
          const option = document.createElement("option");
          option.value = data.supplier.id;
          option.textContent = data.supplier.text;
          option.selected = true;
          select.appendChild(option);
        } else {
          console.warn("❌ supplierSelect not found");
        }
      } else {
        showToast(`❌ ${data.error}`, "danger");
      }
    })
    .catch(err => {
      console.error("Supplier save error:", err);
      showToast("❌ সাপ্লাইয়ার সংরক্ষণে সমস্যা হয়েছে", "danger");
    });
});
// ✅ Supplier Search
$('#supplierSelect').select2({
  placeholder: "Search supplier...",
  minimumInputLength: 2,
  dropdownParent: $('#purchaseModal'),
  ajax: {
    url: "/products/supplier/search/",
    dataType: "json",
    delay: 250,
    data: params => ({ q: params.term }),
    processResults: data => ({ results: data.results })
  }
}).on('select2:open', () => {
  setTimeout(() => document.querySelector('.select2-search__field')?.focus(), 100);
});
function setSupplierInEdit(supplierId) {
  if (!supplierId) return;

  $.ajax({
    url: `/products/supplier/${supplierId}/detail/`,
    dataType: "json",
    success: supplier => {
      // ✅ Compact display like search text
      const displayText = `${supplier.name} (${supplier.company_name || "N/A"}) - ${supplier.mobile || "N/A"}`;
     
      // ✅ Inject into Select2 dropdown
      const option = new Option(displayText, supplier.id, true, true);
      $('#supplierSelect').append(option).trigger('change');
      
       // ✅ Globally accessible
      window.selectedSupplier = supplier;

      // ✅ Optional: show in modal sidebar/header
      const box = document.getElementById("supplierInfoBox");
      if (box && supplier) {
        box.innerHTML = `
          <div><strong>🏢 Company:</strong> ${supplier.company_name || "—"}</div>
          <div><strong>📞 Mobile:</strong> ${supplier.mobile || "—"}</div>
          <div><strong>📍 Address:</strong> ${supplier.address || "—"}</div>
          <div><strong>👤 Contact:</strong> ${supplier.contact_person || "—"} (${supplier.contact_mobile || "—"})</div>
        `;
      } else {
        console.warn("⚠️ supplierInfoBox not found or supplier data missing");
      }
    },
    error: () => {
      showToast("❌ সাপ্লাইয়ার তথ্য লোড হয়নি", "danger");
    }
  });
}

// ✅ Product Search
$('#productSelect').select2({
  placeholder: "Search product...",
  minimumInputLength: 2,
  dropdownParent: $('#purchaseModal'),
  ajax: {
    url: "/products/products/search/",
    dataType: "json",
    delay: 250,
    data: params => ({ q: params.term }),
    processResults: data => ({ results: data.products })
  }
}).on('select2:open', () => {
  setTimeout(() => document.querySelector('.select2-search__field')?.focus(), 100);
});
// ✅ Add Product Row
$('#productSelect').on('select2:select', function (e) {
  const p = e.params.data;

  if (document.querySelector(`#row-${p.id}`)) {
    showToast("⚠️ Already added", "warning");
    $('#productSelect').val(null).trigger("change");
    return;
  }

  const row = document.createElement("tr");
  row.id = `row-${p.id}`;
  row.className = "text-center";

  let qtyCell = "";
  if (p.is_serialized) {
    qtyCell = `
      <button type="button" class="btn btn-sm btn-outline-primary" onclick="openSerialModal(${p.id})" title="Assign serials">🔢 Serial</button>
      <span class="badge bg-info ms-2" id="qty-${p.id}">0</span>
    `;
    serialMap[p.id] = [];
  } else {
    qtyCell = `<input type="number" name="qty_${p.id}" value="1" min="1" class="form-control form-control-sm text-end qty-input">`;
  }

  row.innerHTML = `
    <td>${itemIndex++}</td>
    <td>${p.barcode || "-"}</td>
    <td>${p.name}</td>
    <td>${p.warranty || "-"}</td>
    <td>${qtyCell}</td>
    <td><input type="number" name="price_${p.id}" value="${p.purchase_price}" class="form-control form-control-sm text-end price-input"></td>
    <td><input type="number" name="discount_${p.id}" value="0" class="form-control form-control-sm text-end discount-input"></td>
    <td><span class="item-total fw-bold">৳0.00</span></td>
    <td><button type="button" class="btn btn-sm btn-danger" onclick="removeItemRow(${p.id})">🗑️</button></td>
  `;

  document.querySelector("#itemTable tbody").appendChild(row);
  updateItemCount();
  calculateTotals();

  $('#productSelect').val(null).trigger("change");
  setTimeout(() => document.querySelector('.select2-search__field')?.focus(), 100);
});

function getItemQty(productId) {
  const isSerialized = !!serialMap[productId]; // true if product is serialized

  if (isSerialized) {
    return serialMap[productId]?.length || 0;
  }

  const input = document.querySelector(`[name="qty_${productId}"]`);
  return parseInt(input?.value || 0);
}

// ✅ Remove Product Row
function removeItemRow(pid) {
  const row = document.getElementById(`row-${pid}`);
  if (row) row.remove();
  delete serialMap[pid];
  updateItemCount();
  calculateTotals();
}
function updateItemCount() {
  const tbody = document.querySelector("#itemTable tbody");
  const count = tbody.querySelectorAll("tr").length;
  document.getElementById("itemCount").textContent = count;
}


function openSerialModal(productId) {
  currentProductId = productId;
  const container = document.getElementById("serialContainer");
  const warning = document.getElementById("serialWarning");

  if (!container) return showToast("❌ Serial container missing", "danger");

  container.innerHTML = "";
  warning.style.display = "none";
  warning.textContent = "";

  const serials = serialMap[productId] || [];
  serials.forEach(sn => {
    container.innerHTML += renderSerialInput(sn);
  });

  if (serials.length === 0) addSerialInput();

  bootstrap.Modal.getOrCreateInstance(document.getElementById("serialModal")).show();
}
function renderSerialInput(value = "") {
  return `
    <div class="input-group mb-2 serial-row">
      <input type="text" class="form-control serial-input" value="${value}" placeholder="Enter serial number">
      <span class="input-group-text warranty-preview">⏳</span>
      <button type="button" class="btn btn-outline-danger" onclick="this.closest('.serial-row').remove()">🗑️</button>
    </div>
  `;
}
function addSerialInput() {
  document.getElementById("serialContainer").innerHTML += renderSerialInput();
}
function saveSerials() {
  const inputs = document.querySelectorAll(".serial-input");
  const warning = document.getElementById("serialWarning");

  const serials = Array.from(inputs).map(i => i.value.trim()).filter(Boolean);
  const duplicates = findDuplicateSerials(serials);

  if (serials.length === 0) {
    warning.textContent = "❌ Serial list cannot be empty.";
    warning.style.display = "block";
    return;
  }

  if (duplicates.length > 0) {
    warning.textContent = `⚠️ Duplicate serials: ${duplicates.join(", ")}`;
    warning.style.display = "block";
    return;
  }

  if (serials.some(sn => !/^[a-zA-Z0-9\-_.]+$/.test(sn))) {
    warning.textContent = "❌ Invalid characters in serials.";
    warning.style.display = "block";
    return;
  }

  serialMap[currentProductId] = serials;

  document.getElementById(`qty-${currentProductId}`).textContent = serials.length;
  updateItemTotal(currentProductId);
  calculateTotals();

  bootstrap.Modal.getInstance(document.getElementById("serialModal")).hide();
}
function findDuplicateSerials(list) {
  const seen = new Set();
  const dupes = [];

  list.forEach(sn => {
    if (seen.has(sn)) dupes.push(sn);
    seen.add(sn);
  });

  return dupes;
}
document.addEventListener("input", function (e) {
  if (e.target.classList.contains("serial-input")) {
    const preview = e.target.closest(".serial-row")?.querySelector(".warranty-preview");
    const sn = e.target.value.trim();

    if (sn.length < 3) {
      preview.textContent = "⏳";
      return;
    }

    fetch(`/products/serial/warranty-preview/?sn=${encodeURIComponent(sn)}`)
      .then(res => res.json())
      .then(data => {
        preview.textContent = data.warranty || "❓";
      })
      .catch(() => {
        preview.textContent = "⚠️";
      });
  }
});

function updateItemTotal(productId) {
  const qty = getItemQty(productId);
  const price = parseFloat(document.querySelector(`[name="price_${productId}"]`)?.value || 0);
  const discount = parseFloat(document.querySelector(`[name="discount_${productId}"]`)?.value || 0);
  const total = (price * qty) - discount;

  const totalCell = document.querySelector(`#row-${productId} .item-total`);
  if (totalCell) totalCell.textContent = `৳${total.toFixed(2)}`;
}
function calculateTotals() {
  let subtotal = 0;

  // 🔹 Loop through item rows
  document.querySelectorAll("#itemTable tbody tr").forEach(row => {
    const pid = row.id.replace("row-", "");
    const qty = getItemQty(pid);

    // 🔹 Update badge qty
    const badge = row.querySelector(".badge");
    if (badge) badge.textContent = qty;

    // 🔹 Update row total
    updateItemTotal(pid);

    // 🔹 Extract total from row
    const totalText = row.querySelector(".item-total")?.textContent || "৳0.00";
    const total = parseFloat(totalText.replace(/[^\d.-]/g, "")) || 0;

    subtotal += total;
  });

  // 🔹 Set subtotal
  subtotal = Math.max(subtotal, 0); // prevent negative
  document.getElementById("subtotal").value = subtotal.toFixed(2);

  // 🔹 Get discount
  const discountValue = parseFloat(document.getElementById("discountValue")?.value || 0);
  const discountType = document.getElementById("discountType")?.value;

  let discount = 0;

  if (discountType === "percent") {
    const percent = Math.min(discountValue, 100); // cap at 100%
    discount = (subtotal * percent) / 100;
  } else {
    discount = discountValue;
  }

  discount = Math.max(discount, 0); // prevent negative
  const grandTotal = Math.max(subtotal - discount, 0); // prevent negative total

  // 🔹 Update UI
  document.getElementById("grandTotal").value = grandTotal.toFixed(2);
}

document.addEventListener("input", e => {
  if (
    e.target.matches(".qty-input") ||
    e.target.matches(".price-input") ||
    e.target.matches(".discount-input") ||
    e.target.id === "discountValue" ||
    e.target.id === "discountType"
  ) {
    calculateTotals();
  }
});
document.addEventListener("keydown", function (e) {
  if (
    e.key === "Enter" &&
    (
      e.target.matches("#discountValue") ||
      e.target.matches("#discountType") ||
      e.target.matches(".qty-input") ||
      e.target.matches(".price-input") ||
      e.target.matches(".discount-input") ||
      e.target.matches(".note-input")
    )
  ) {
    e.preventDefault();
    calculateTotals();
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("purchaseForm");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearFieldErrors();

    const errors = [];

    // 🔹 Validate Supplier
    const supplierSelect = document.getElementById("supplierSelect");
    const supplierId = supplierSelect?.value;
    if (!supplierId) {
      errors.push({ field: "supplierSelect", message: "Supplier is required" });
    }

    // 🔹 Validate Date
    const dateInput = document.getElementById("purchaseDate");
    if (!dateInput?.value) {
      errors.push({ field: "purchaseDate", message: "Date is required" });
    }

    // 🔹 Validate Product Rows
    const itemRows = document.querySelectorAll("#itemTable tbody tr");
    if (itemRows.length === 0) {
      errors.push({ field: "productSelect", message: "At least one product is required" });
    }

    // 🔹 Validate Serialized Products
    for (const pid in serialMap) {
      const serials = serialMap[pid];
      if (Array.isArray(serials) && serials.length === 0) {
        errors.push({ field: `qty-${pid}`, message: "Serials required for this product" });
      }
    }

    // 🔹 Show Errors
    if (errors.length > 0) {
      errors.forEach(err => highlightFieldError(err.field, err.message));
      showToast("❌ Please fix the highlighted fields", "danger");
      document.querySelector("#purchaseModal .modal-body").scrollTop = 0;
      return;
    }

    // 🔹 Prepare FormData
    const formData = new FormData(form);
    const purchaseId = form.querySelector("#purchaseId")?.value;
    const isEdit = !!purchaseId;

    const url = isEdit
      ? `/products/purchase/${purchaseId}/update/`
      : `/products/purchase/create/`;

    formData.append("supplier_id", supplierId);
    formData.append("subtotal", document.getElementById("subtotal").value);
    formData.append("total_discount", document.getElementById("discountValue").value);
    formData.append("discount_type", document.getElementById("discountType").value);
    formData.append("total", document.getElementById("grandTotal").value);
    formData.append("serials", JSON.stringify(serialMap));

    // 🔹 Submit
    fetch(url, {
      method: "POST",
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(isEdit ? "✅ Purchase updated" : "✅ Purchase saved", "success");
          bootstrap.Modal.getInstance(document.getElementById("purchaseModal")).hide();
          resetPurchaseForm();

          // 🔁 Optional redirect or refresh
          setTimeout(() => {
            window.location.href = "/products/purchase/";
          }, 1500);
        } else {
          showToast("❌ " + (data.message || "Save failed"), "danger");
        }
      })
      .catch(err => {
        console.error("Purchase error:", err);
        showToast("❌ Unexpected error", "danger");
      });
  });
});

function deletePurchase(purchaseId) {
  if (!confirm("❌ আপনি কি নিশ্চিতভাবে এই পারচেস ডিলিট করতে চান?")) return;

  fetch(`/products/purchase/${purchaseId}/delete/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken()
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast("🗑️ পারচেস ডিলিট হয়েছে", "success");
        document.getElementById(`purchase-row-${purchaseId}`)?.remove();
      } else {
        showToast("❌ " + data.message, "danger");
      }
    })
    .catch(() => showToast("❌ নেটওয়ার্ক সমস্যা", "danger"));
}

function handleValidationError(message) {
  showToast("❌ " + message, "danger");

  if (message.includes("serials but none provided")) {
    const pid = extractProductIdFromMessage(message);
    highlightFieldError(`qty-${pid}`, message);
  }

  if (message.includes("Duplicate serial")) {
    highlightFieldError("serialContainer", message);
  }

  if (message.includes("Invalid date")) {
    highlightFieldError("purchaseDate", message);
  }

  document.querySelector("#purchaseModal .modal-body").scrollTop = 0;
}function highlightFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  if (!field) return;

  field.classList.add("is-invalid");
  field.setAttribute("title", message);

  const feedback = document.createElement("div");
  feedback.className = "invalid-feedback";
  feedback.textContent = message;

  if (!field.nextElementSibling?.classList.contains("invalid-feedback")) {
    field.parentNode.appendChild(feedback);
  }

  field.scrollIntoView({ behavior: "smooth", block: "center" });
}
function clearFieldErrors() {
  document.querySelectorAll(".is-invalid").forEach(el => {
    el.classList.remove("is-invalid");
    el.removeAttribute("title");
  });

  document.querySelectorAll(".invalid-feedback").forEach(el => el.remove());
}
function showToast(message, type = "info", timeout = 4000) {
  const toastId = "toast-" + Date.now();
  const bgClass = {
    success: "bg-success",
    danger: "bg-danger",
    warning: "bg-warning",
    info: "bg-info"
  }[type] || "bg-secondary";

  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-white ${bgClass} border-0 show`;
  toast.id = toastId;
  toast.setAttribute("role", "alert");
  toast.setAttribute("aria-live", "assertive");
  toast.setAttribute("aria-atomic", "true");

  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;

  document.getElementById("toastContainer").appendChild(toast);

  setTimeout(() => {
    toast.classList.remove("show");
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 500);
  }, timeout);
}
function extractProductIdFromMessage(message) {
  const match = message.match(/product.*?(\d+)/);
  return match ? match[1] : null;
}
function resetPurchaseForm() {
  // 🔹 Clear all input fields
  document.getElementById("purchaseForm").reset();

  // 🔹 Clear select2 dropdowns
  $('#supplierSelect').val(null).trigger("change");
  $('#productSelect').val(null).trigger("change");

  // 🔹 Clear item table
  document.querySelector("#itemTable tbody").innerHTML = "";
  itemIndex = 1;

  // 🔹 Reset totals
  document.getElementById("subtotal").value = "0.00";
  document.getElementById("discountValue").value = "";
  document.getElementById("grandTotal").value = "0.00";

  // 🔹 Reset serial map
  serialMap = {};

  // 🔹 Clear validation errors
  clearFieldErrors();

  // 🔹 Optional toast
  showToast("🔄 Purchase form refreshed", "info");
}
document.getElementById("purchaseModal").addEventListener("hidden.bs.modal", resetPurchaseForm);

$(document).ready(function () {
  const table = $('#purchaseTable').DataTable({
    dom: "<'row mb-2'<'col-md-6 d-flex align-items-center'B><'col-md-6 text-end'f>>" +
         "<'row'<'col-12'tr>>" +
         "<'row mt-2'<'col-md-6'i><'col-md-6 text-end'p>>",
    buttons: [
      { extend: 'csv', className: 'btn btn-sm btn-outline-secondary me-2', text: '⬇️ CSV' },
      { extend: 'excel', className: 'btn btn-sm btn-outline-success me-2', text: '📊 Excel' },
      { extend: 'pdf', className: 'btn btn-sm btn-outline-danger me-2', text: '📄 PDF' },
      { extend: 'print', className: 'btn btn-sm btn-outline-primary', text: '🖨️ Print' }
    ],
    pageLength: 25,
    language: {
      search: "",  // Remove default label
      searchPlaceholder: "🔍 সার্চ করুন...",
      lengthMenu: "_MENU_ টি রেকর্ড দেখান",
      info: "_TOTAL_ টি রেকর্ডের মধ্যে _START_ থেকে _END_ দেখানো হচ্ছে",
      paginate: {
        previous: "← পূর্ববর্তী",
        next: "পরবর্তী →"
      },
      emptyTable: "❌ কোনো তথ্য পাওয়া যায়নি"
    },
    columnDefs: [
      { orderable: false, targets: -1 }
    ]
  });

  // 🔍 Supplier Filter
  $('#supplierFilter').on('change', function () {
    table.column(2).search(this.value).draw();
  });

  // 🔍 Status Filter
  $('#statusFilter').on('change', function () {
    const val = this.value;
    if (val === "Paid") {
      table.column(6).search("Paid").draw();
    } else if (val === "Due") {
      table.column(6).search("Due").draw();
    } else {
      table.column(6).search("").draw();
    }
  });
});

