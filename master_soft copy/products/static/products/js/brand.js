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

function clearBrandForm() {
  document.getElementById("brandForm").reset();
  document.getElementById("brandId").value = "";
  document.getElementById("deleteBrandBtn")?.classList.add("d-none");
  document.getElementById("logoPreview").innerHTML = "";
  document.getElementById("brandForm").classList.remove("was-validated");
}

document.getElementById("brandLogo").addEventListener("change", function () {
  const file = this.files[0];
  const preview = document.getElementById("logoPreview");
  preview.innerHTML = "";
  if (file && file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.className = "img-thumbnail mt-2";
    img.style.maxHeight = "100px";
    preview.appendChild(img);
  }
});

document.getElementById("brandForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const form = this;

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const id = document.getElementById("brandId").value;
  const url = id ? `/products/brand/${id}/edit/` : `/products/brand/create/`;
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
        throw new Error("Server error");
      });
    }
    return res.json();
  })
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("brandModal")).hide();
      clearBrandForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    console.error("❌ AJAX Error:", err);
    showToast("❌ সংরক্ষণ করতে সমস্যা হয়েছে", "danger");
  });
});

document.querySelectorAll(".edit-brand-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const id = this.dataset.id;
    fetch(`/products/brand/${id}/json/`)
      .then(res => {
        if (!res.ok) {
          return res.json().then(data => {
            showToast(`❌ ${data.error || 'ডেটা লোড করতে সমস্যা হয়েছে'}`, "danger");
            throw new Error("Fetch failed");
          });
        }
        return res.json();
      })
      .then(data => {
        if (data.success) {
          const b = data.brand;
          document.getElementById("brandId").value = b.id;
          document.getElementById("brandName").value = b.name;
          document.getElementById("brandCountry").value = b.country || "";
          document.getElementById("brandSupport_contact").value = b.support_contact || "";
          document.getElementById("is_active").value = b.is_active ? "true" : "false";

          document.getElementById("deleteBrandBtn").classList.remove("d-none");

          const preview = document.getElementById("logoPreview");
          preview.innerHTML = "";
          if (b.logo_url) {
            const img = document.createElement("img");
            img.src = b.logo_url;
            img.className = "img-thumbnail mt-2";
            img.style.maxHeight = "100px";
            preview.appendChild(img);
          }

          new bootstrap.Modal(document.getElementById("brandModal")).show();
        } else {
          showToast(`❌ ${data.error}`, "danger");
        }
      })
      .catch(err => {
        console.error("❌ Edit Fetch Error:", err);
        showToast("❌ ডেটা লোড করতে সমস্যা হয়েছে", "danger");
      });
  });
});
document.getElementById("deleteBrandBtn").addEventListener("click", function () {
  const id = document.getElementById("brandId").value;
  if (!confirm("❗ আপনি কি নিশ্চিতভাবে ডিলিট করতে চান?")) return;

  fetch(`/products/brand/${id}/delete/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() }
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => {
        showToast(`❌ ${data.error || 'ডিলিট করতে সমস্যা হয়েছে'}`, "danger");
        throw new Error("Delete failed");
      });
    }
    return res.json();
  })
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("brandModal")).hide();
      document.getElementById(`brandRow${id}`)?.remove();
      clearBrandForm();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    console.error("❌ Delete Error:", err);
    showToast("❌ ডিলিট করতে সমস্যা হয়েছে", "danger");
  });
});
