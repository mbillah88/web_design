// 🔹 CSRF Helper
function getCSRF() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// 🔹 Toast Feedback
function showToast(msg, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast text-bg-${type} border-0 show mb-2`;
  toast.innerHTML = `<div class="d-flex">
    <div class="toast-body">${msg}</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto"
      onclick="this.parentElement.parentElement.remove()"></button>
  </div>`;
  document.getElementById('toastContainer').appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// 🔹 Clear Form
function clearProductForm() {
  document.getElementById("productForm").reset();
  document.getElementById("productId").value = "";
  document.getElementById("deleteProductBtn")?.classList.add("d-none");
  document.getElementById("productForm").classList.remove("was-validated");
}

// 🔹 Submit Handler
document.getElementById("productForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const form = this;

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const id = document.getElementById("productId").value;
  const url = id ? `/products/${id}/edit/` : `/products/create/`;
  const formData = new FormData(form);

  fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => {
        showToast(`❌ ${data.error || 'সার্ভার ত্রুটি'}`, "danger");
        throw new Error(data.error || "Server error");
      });
    }
    return res.json();
  })
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("productModal")).hide();
      clearProductForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    showToast(`❌ ${err.message}`, "danger");
  });
});

// 🔹 Edit Button Binding
document.querySelectorAll(".edit-product-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const id = this.dataset.id;
    fetch(`/products/${id}/json/`)
      .then(res => res.json())
      .then(data => {
        if (!data.success) {
          showToast(`❌ ${data.error}`, "danger");
          return;
        }

        const modalEl = document.getElementById("productModal");
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        setTimeout(() => {
        const p = data.product;

        const fields = {
          productId: p.id,
          productName: p.name,
          productModel: p.model,
          productDescription: p.description,
          productBrand: p.brand,
          productCategory: p.category,
          productPurchasePrice: p.purchase_price,
          productSalePrice: p.sale_price,
          productDiscountPrice: p.discount_price,
          productVatPercent: p.vat_percent,
          productStockAlert: p.stock_alert,
          productBarcode: p.barcode,
          productUnit: p.unit,
          productWarranty: p.warranty,
          productWarrantyDurationMonths: p.warranty_duration_months,
          productServiceIntervalDays: p.service_interval_days,
          productIsActive: p.is_active ? "true" : "false",
          productIsSerialized: p.is_serialized ? "true" : "false",
          productRequiresBatch: p.requires_batch ? "true" : "false",
          productIsReturnable: p.is_returnable ? "true" : "false",
          productIsServiceable: p.is_serviceable ? "true" : "false"
        };

        // ✅ Image preview logic
        const preview = document.getElementById("imagePreview");
        if (preview) {
          if (p.image) {
            preview.src = p.image;
            preview.classList.remove("d-none");
          } else {
            preview.src = "/static/images/no-image.png"; // ✅ fallback image
            preview.classList.remove("d-none");
          }
        }

        for (const [id, value] of Object.entries(fields)) {
          const el = document.getElementById(id);
          if (!el) {
            console.warn(`⚠️ Missing field: ${id}`);
            continue;
          }

          // Handle number inputs safely
          if (el.type === "number") {
            el.value = value !== undefined && value !== null ? value : "";
          } else {
            el.value = value ?? "";
          }
        }


        document.getElementById("deleteProductBtn")?.classList.remove("d-none");
      }, 200);
 // Delay to ensure modal DOM is visible
      })
      .catch(err => {
        console.error("❌ Edit Fetch Error:", err);
        showToast("❌ ডেটা লোড করতে সমস্যা হয়েছে", "danger");
      });
  });
});

// 🔹 Delete Handler
document.getElementById("deleteProductBtn").addEventListener("click", function () {
  const id = document.getElementById("productId").value;
  if (!id) {
    showToast("❌ পণ্য ID পাওয়া যায়নি", "danger");
    return;
  }

  if (!confirm("❗ আপনি কি নিশ্চিতভাবে ডিলিট করতে চান?")) return;

  fetch(`/products/${id}/delete/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("productModal")).hide();
      document.getElementById(`productRow${id}`)?.remove();
      clearProductForm();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    console.error("❌ Delete Error:", err);
    showToast("❌ ডিলিট করতে সমস্যা হয়েছে", "danger");
  });
});

// search filter
function filterTable() {
  const brand = document.getElementById("brandFilter").value.toLowerCase();
  const category = document.getElementById("categoryFilter").value.toLowerCase();
  const code = document.querySelector('input[placeholder="Search code"]').value.toLowerCase();
  const barcode = document.getElementById("barcodeSearch").value.toLowerCase();
  const name = document.querySelector('input[placeholder="Search name"]').value.toLowerCase();
  const model = document.querySelector('input[placeholder="Search model"]').value.toLowerCase();

  document.querySelectorAll("#productTableBody tr").forEach(row => {
    const cells = row.querySelectorAll("td");
    const match =
      (!brand || cells[6].textContent.toLowerCase().includes(brand)) &&     // ✅ Brand
      (!category || cells[7].textContent.toLowerCase().includes(category)) && // ✅ Category
      (!code || cells[2].textContent.toLowerCase().includes(code)) &&       // ✅ Product Code
      (!barcode || cells[3].textContent.toLowerCase().includes(barcode)) && // ✅ Barcode
      (!name || cells[4].textContent.toLowerCase().includes(name)) &&       // ✅ Name
      (!model || cells[5].textContent.toLowerCase().includes(model));    

    row.style.display = match ? "" : "none";
  });
}

document.querySelectorAll("thead input, thead select").forEach(el => {
  el.addEventListener("input", filterTable);
  el.addEventListener("change", filterTable);
});

function exportTableToCSV() {
  let csv = [];
  const rows = document.querySelectorAll("table tr");
  rows.forEach(row => {
    const cols = row.querySelectorAll("th, td");
    const rowData = Array.from(cols).map(col => `"${col.innerText.trim()}"`);
    csv.push(rowData.join(","));
  });

  const blob = new Blob([csv.join("\n")], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "products.csv";
  link.click();
}

let isAutoBarcode = false;

function toggleBarcodeMode() {
  isAutoBarcode = !isAutoBarcode;

  const barcodeInput = document.getElementById("productBarcode");
  const hint = document.getElementById("barcodeModeHint");

  if (isAutoBarcode) {
    barcodeInput.value = "";
    barcodeInput.readOnly = true;
    hint.textContent = "বর্তমানে: অটো বারকোড মোড (সেভ করার সময় জেনারেট হবে)";
  } else {
    barcodeInput.readOnly = false;
    hint.textContent = "বর্তমানে: ম্যানুয়াল মোড";
  }
}


// 🔹 Barcode Scanner Integration
let barcodeScannerInstance;
window.openBarcodeModal = function () {
  const modalEl = document.getElementById("barcodeModal");
  modalEl.classList.add("show");
  modalEl.style.display = "block";
  modalEl.style.zIndex = "1060";

  barcodeScannerInstance = new Html5QrcodeScanner("barcodeScanner", {
    fps: 10,
    qrbox: 250,
    rememberLastUsedCamera: true,
    supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
  });

  barcodeScannerInstance.render((decodedText) => {
    checkBarcodeUniqueness(decodedText);
    closeBarcodeModal();
  });
};

function closeBarcodeModal() {
  const modalEl = document.getElementById("barcodeModal");
  modalEl.classList.remove("show");
  modalEl.style.display = "none";
  if (barcodeScannerInstance) {
    barcodeScannerInstance.clear();
    barcodeScannerInstance = null;
  }
}

function checkBarcodeUniqueness(barcode) {
  fetch(`/products/check-barcode/?barcode=${encodeURIComponent(barcode)}`)
    .then(res => res.json())
    .then(data => {
      if (data.valid) {
        document.getElementById("productBarcode").value = barcode;
        showToast(`✅ বারকোড স্ক্যান হয়েছে: ${barcode}`);
      } else {
        showToast(`❌ বারকোড '${barcode}' ইতিমধ্যে আছে`, "danger");
        document.getElementById("productBarcode").classList.add("is-invalid");
      }
    })
    .catch(err => {
      console.error("❌ Barcode Check Error:", err);
      showToast("❌ বারকোড যাচাই করতে সমস্যা হয়েছে", "danger");
    });
}
function handleBarcodeScan(decodedText) {
  document.getElementById("barcodeSearch").value = decodedText;
  filterTable();
  showToast(`✅ Barcode scanned: ${decodedText}`);
}
document.addEventListener("DOMContentLoaded", function () {
  const dropZone = document.getElementById("imageDropZone");
  const fileInput = document.getElementById("productImage");
  const preview = document.getElementById("imagePreview");

  // 🔹 Click to open file picker
  dropZone.addEventListener("click", () => fileInput.click());

  // 🔹 File selected
  fileInput.addEventListener("change", handleImage);

  // 🔹 Drag events
  dropZone.addEventListener("dragover", e => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      handleImage();
    }
  });

  // 🔹 Preview + Validation
  function handleImage() {
    const file = fileInput.files[0];
    if (!file) return;

    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    const maxSize = 2 * 1024 * 1024; // 2MB

    if (!validTypes.includes(file.type)) {
      showToast("❌ শুধুমাত্র JPG, PNG, বা WEBP ফাইল অনুমোদিত", "danger");
      fileInput.value = "";
      preview.classList.add("d-none");
      return;
    }

    if (file.size > maxSize) {
      showToast("❌ ছবির সাইজ 2MB এর বেশি হতে পারবে না", "danger");
      fileInput.value = "";
      preview.classList.add("d-none");
      return;
    }

    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.classList.remove("d-none");
    };
    reader.readAsDataURL(file);
  }
});
