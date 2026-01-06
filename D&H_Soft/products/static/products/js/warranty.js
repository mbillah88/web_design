function getCSRF() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

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

function clearWarrantyForm() {
  const form = document.getElementById("warrantyForm");
  form.reset();
  form.classList.remove("was-validated");
  document.getElementById("warrantyId").value = "";
  document.getElementById("deleteWarrantyBtn")?.classList.add("d-none");
}

function openWarrantyModal() {
  clearWarrantyForm();
  bootstrap.Modal.getOrCreateInstance(document.getElementById("warrantyModal")).show();
}

// ✅ Submit Warranty Form
document.getElementById("warrantyForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const form = this;
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const id = document.getElementById("warrantyId").value;
  const url = id ? `/products/warranty/${id}/edit/` : `/products/warranty/create/`;

  const formData = new URLSearchParams(new FormData(form));

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRF(),
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("warrantyModal")).hide();
      clearWarrantyForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  });
});

// ✅ Edit Warranty
document.querySelectorAll(".edit-warranty-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const id = this.dataset.id;
    fetch(`/products/warranty/${id}/json/`)
      .then(res => res.json())
      .then(data => {
        if (!data.success) {
          showToast(`❌ ${data.error}`, "danger");
          return;
        }

        const w = data.warranty;
        document.getElementById("warrantyId").value = w.id;
        document.getElementById("warrantyName").value = w.name;
        document.getElementById("warrantyType").value = w.type;
        document.getElementById("duration_value").value = w.duration_value;
        document.getElementById("duration_unit").value = w.duration_unit;
        document.getElementById("is_lifetime").value = w.is_lifetime ? "true" : "false";
        document.getElementById("terms").value = w.terms;
        document.getElementById("is_active").value = w.is_active ? "true" : "false";

        document.getElementById("deleteWarrantyBtn")?.classList.remove("d-none");
        bootstrap.Modal.getOrCreateInstance(document.getElementById("warrantyModal")).show();
      });
  });
});

// ✅ Delete Warranty
document.getElementById("deleteWarrantyBtn").addEventListener("click", function () {
  const id = document.getElementById("warrantyId").value;
  if (!confirm("❗ আপনি কি নিশ্চিতভাবে ডিলিট করতে চান?")) return;

  fetch(`/products/warranty/${id}/delete/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("warrantyModal")).hide();
      document.getElementById(`warrantyRow${id}`)?.remove();
      clearWarrantyForm();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  });
});
