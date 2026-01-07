function getCSRF() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// ✅ Open Purchase Modal
function openPurchaseModal() {
  const form = document.getElementById("purchaseForm");
  form.reset();
  bootstrap.Modal.getOrCreateInstance(document.getElementById("purchaseModal")).show();
}

// ✅ Submit Purchase Form (AJAX)
document.getElementById("submitPurchase").addEventListener("click", function () {
  const form = document.getElementById("purchaseForm");

  const itemCount = document.querySelectorAll("#itemTable tbody tr").length;
  if (itemCount === 0) {
    showInputToast("⚠️ অন্তত একটি প্রোডাক্ট সিলেক্ট করুন", "warning");
    return;
  }

  const formData = new FormData(form);
  formData.append("item_count", itemCount);

  fetch("/purchase/create/", {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
  .then(res => res.ok ? res.json() : Promise.reject("Invalid response"))
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("purchaseModal")).hide();
      form.reset();
      document.querySelector("#itemTable tbody").innerHTML = "";
      updateDueAmount();
      location.reload();
    } else {
      showToast(`❌ ${data.error || "সাবমিট ব্যর্থ হয়েছে"}`, "danger");
    }
  })
  .catch(err => {
    console.error("❌ Submit error:", err);
    showToast("❌ সাবমিট করতে সমস্যা হয়েছে", "danger");
  });
});

// ✅ Open Payment Modal
function openPaymentModal(purchaseId) {
  document.getElementById("paymentPurchaseId").value = purchaseId;
  bootstrap.Modal.getOrCreateInstance(document.getElementById("paymentModal")).show();
}

// ✅ Submit Payment Form
document.getElementById("paymentForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(this);

  fetch("/purchase/payment/", {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    showToast(data.message);
    bootstrap.Modal.getInstance(document.getElementById("paymentModal")).hide();
    location.reload();
  });
});

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

      // ✅ Refresh supplier dropdown
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
// ✅ Debounced supplier search
function bindSupplierSearch(inputElement) {
  let supplierTimer;

  inputElement.addEventListener("input", function () {
    clearTimeout(supplierTimer);
    const query = this.value.trim();
    if (query.length < 2) return;

    supplierTimer = setTimeout(() => {
      fetch(`/products/supplier/search/?q=${encodeURIComponent(query)}`)
        .then(res => res.ok ? res.json() : Promise.reject("Invalid response"))
        .then(data => showSupplierSuggestions(data.results))
        .catch(() => showToast("❌ সাপ্লাইয়ার খুঁজতে সমস্যা হয়েছে", "danger"));
    }, 300);
  });
}
// ✅ Show suggestions
function showSupplierSuggestions(suppliers) {
  const container = document.getElementById("supplierSuggestions");
  container.innerHTML = "";
  container.classList.remove("d-none");

  if (suppliers.length === 0) {
    container.innerHTML = `<div class="list-group-item text-muted">কোন সাপ্লাইয়ার পাওয়া যায়নি</div>`;
    return;
  }

  // ✅ Auto-select if only one match
  if (suppliers.length === 1) {
    selectSupplier(suppliers[0]);
    return;
  }

  suppliers.forEach(s => {
    const item = document.createElement("button");
    item.className = "list-group-item list-group-item-action";
    item.textContent = s.text;
    item.onclick = () => selectSupplier(s);
    container.appendChild(item);
  });
}

// ✅ Select supplier
function selectSupplier(supplier) {
  document.getElementById("supplierSearch").value = supplier.text;
  document.getElementById("supplierId").value = supplier.id;
  document.getElementById("supplierSuggestions").classList.add("d-none");
}

// ✅ Keyboard navigation
document.getElementById("supplierSearch").addEventListener("keydown", function (e) {
  const items = document.querySelectorAll("#supplierSuggestions .list-group-item-action");
  if (!items.length) return;

  let index = [...items].findIndex(item => item.classList.contains("active"));

  if (e.key === "ArrowDown") {
    e.preventDefault();
    index = (index + 1) % items.length;
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    index = (index - 1 + items.length) % items.length;
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (index >= 0) items[index].click();
    else items[0].click();
    return;
  } else return;

  items.forEach(item => item.classList.remove("active"));
  items[index].classList.add("active");
  items[index].scrollIntoView({ block: "nearest" });
});
// ✅ Toast near input
function showInputToast(message, type = "danger") {
  const area = document.getElementById("productToastArea");
  if (!area) return;
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-white bg-${type} border-0`;
  toast.role = "alert";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body small">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  area.appendChild(toast);
  new bootstrap.Toast(toast).show();
  setTimeout(() => toast.remove(), 4000);
}

// ✅ Prevent Enter from submitting form
document.getElementById("productSearch").addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
    const items = document.querySelectorAll("#productSuggestions .list-group-item-action");
    if (items.length === 0) {
      showInputToast("⚠️ প্রোডাক্ট সিলেক্ট করুন", "warning");
      return;
    }
    const active = [...items].find(i => i.classList.contains("active")) || items[0];
    active.click();
  }

  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    const items = document.querySelectorAll("#productSuggestions .list-group-item-action");
    if (items.length === 0) return;
    let index = [...items].findIndex(i => i.classList.contains("active"));
    index = e.key === "ArrowDown" ? (index + 1) % items.length : (index - 1 + items.length) % items.length;
    items.forEach(i => i.classList.remove("active"));
    items[index].classList.add("active");
    items[index].scrollIntoView({ block: "nearest" });
    e.preventDefault();
  }
});

// ✅ Debounced search
let searchTimer;
document.getElementById("productSearch").addEventListener("input", function () {
  clearTimeout(searchTimer);
  const query = this.value.trim();
  if (query.length < 2) return;
  searchTimer = setTimeout(() => {
    fetch(`/products/products/search/?q=${encodeURIComponent(query)}`)
      .then(res => res.ok ? res.json() : Promise.reject("Invalid response"))
      .then(data => showProductSuggestions(this, data.products))
      .catch(() => showInputToast("❌ সার্চে সমস্যা হয়েছে"));
  }, 300);
});

// ✅ Show suggestions
function showProductSuggestions(input, products) {
  const container = document.getElementById("productSuggestions");
  container.innerHTML = "";
  container.classList.remove("d-none");
  if (products.length === 0) {
    container.innerHTML = `<div class="list-group-item text-muted">কোন প্রোডাক্ট পাওয়া যায়নি</div>`;
    return;
  }
  products.forEach(p => {
    const item = document.createElement("button");
    item.className = "list-group-item list-group-item-action";
    item.textContent = `${p.name} (${p.model})`;
    item.onclick = () => {
      if (isProductAlreadyAdded(p.id)) {
        showInputToast("⚠️ এই প্রোডাক্ট ইতিমধ্যে যোগ করা হয়েছে", "warning");
        return;
      }
      addItemRow(p);
            input.value = "";
      container.classList.add("d-none");

      // ✅ Auto-focus quantity input
      setTimeout(() => {
        const qtyInput = document.querySelector(`#itemTable tbody tr:last-child .qty-input`);
        if (qtyInput) qtyInput.focus();
      }, 100);
    };
    container.appendChild(item);
  });
}

// ✅ Check duplicate
function isProductAlreadyAdded(productId) {
  return [...document.querySelectorAll("[name^='product_id_']")].some(input => input.value == productId);
}

// ✅ Add item row
function addItemRow(product = null) {
  const tbody = document.querySelector("#itemTable tbody");
  const index = tbody.children.length;

  const row = document.createElement("tr");
  row.innerHTML = `
    <td>
      <input type="text" name="product_${index}" class="form-control product-input" value="${product?.name || ''}" required>
      <input type="hidden" name="product_id_${index}" value="${product?.id || ''}">
    </td>
    <td><input type="number" name="quantity_${index}" class="form-control qty-input" value="1" min="1" required></td>
    <td><input type="number" name="unit_price_${index}" class="form-control price-input" value="${product?.price || 0}" min="0" required></td>
    <td><input type="number" name="discount_${index}" class="form-control discount-input" value="0" min="0"></td>
    <td><span class="item-total fw-bold">৳ 0.00</span></td>
    <td><button type="button" class="btn btn-sm btn-warning" onclick="editItemRow(this)">✏️</button></td>
    <td><button type="button" class="btn btn-sm btn-danger" onclick="removeItemRow(this)">🗑️</button></td>
  `;
  tbody.appendChild(row);
  attachItemEvents(row);
  updateItemTotal(row);
}

// ✅ Attach events
function attachItemEvents(row) {
  row.querySelectorAll(".qty-input, .price-input, .discount-input").forEach(input => {
    input.addEventListener("input", () => updateItemTotal(row));
  });
}

// ✅ Update total
function updateItemTotal(row) {
  const qty = parseFloat(row.querySelector(".qty-input").value) || 0;
  const price = parseFloat(row.querySelector(".price-input").value) || 0;
  const discount = parseFloat(row.querySelector(".discount-input").value) || 0;
  const total = (qty * price) - discount;
  row.querySelector(".item-total").textContent = `৳ ${total.toFixed(2)}`;
  updateDueAmount();
}

// ✅ Update due amount
function updateDueAmount() {
  let subtotal = 0;
  document.querySelectorAll("#itemTable tbody tr").forEach(row => {
    const qty = parseFloat(row.querySelector(".qty-input").value) || 0;
    const price = parseFloat(row.querySelector(".price-input").value) || 0;
    const discount = parseFloat(row.querySelector(".discount-input").value) || 0;
    subtotal += (qty * price) - discount;
  });

  document.querySelector("[name='subtotal']").value = subtotal.toFixed(2);

  const invoiceDiscount = parseFloat(document.querySelector("[name='total_discount']")?.value || 0);
  const paid = parseFloat(document.querySelector("[name='paid']")?.value || 0);
  const due = Math.max(subtotal - invoiceDiscount - paid, 0);
  document.getElementById("dueAmount").textContent = `৳ ${due.toFixed(2)}`;
}

// ✅ Remove row
function removeItemRow(btn) {
  btn.closest("tr").remove();
  updateDueAmount();
}

// ✅ Edit row
function editItemRow(btn) {
  const input = btn.closest("tr").querySelector(".product-input");
  if (input) input.focus();
}
