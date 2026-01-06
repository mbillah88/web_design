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

function clearUnitForm() {
  document.getElementById("unitForm").reset();
  document.getElementById("unitId").value = "";
  document.getElementById("deleteUnitBtn")?.classList.add("d-none");
  document.getElementById("unitForm").classList.remove("was-validated");
}

document.getElementById("unitForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const form = this;

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const id = document.getElementById("unitId").value;
  const url = id ? `/products/unit/${id}/edit/` : `/products/unit/create/`;
  const formData = new FormData(form);

  fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() },
    body: formData
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => {
        const msg = data.error || "সার্ভার ত্রুটি";
        showToast(`❌ ${msg}`, "danger");
        throw new Error(msg); // pass to catch
      });
    }
    return res.json();
  })
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("unitModal")).hide();
      clearUnitForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    if (err.message === "Server error") return;
    showToast(`❌ ${err.message}`, "danger");
  });
});

document.querySelectorAll(".edit-unit-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const id = this.dataset.id;
    fetch(`/products/unit/${id}/json/`)
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
          const u = data.unit;
          document.getElementById("unitId").value = u.id;
          document.getElementById("unitName").value = u.name;
          document.getElementById("unitSymbol").value = u.symbol || "";
          document.getElementById("unitFactor").value = u.conversion_factor || "1.0000";
          document.getElementById("unitActive").value = u.is_active ? "true" : "false";

          document.getElementById("deleteUnitBtn").classList.remove("d-none");
          new bootstrap.Modal(document.getElementById("unitModal")).show();
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

document.getElementById("deleteUnitBtn").addEventListener("click", function () {
  const id = document.getElementById("unitId").value;
  if (!id) {
    showToast("❌ ইউনিট ID পাওয়া যায়নি", "danger");
    return;
  }

  if (!confirm("❗ আপনি কি নিশ্চিতভাবে ডিলিট করতে চান?")) return;

  fetch(`/products/unit/${id}/delete/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("unitModal")).hide();
      document.getElementById(`unitRow${id}`)?.remove();
      clearUnitForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  })
  .catch(err => {
    console.error("❌ Delete Error:", err);
    showToast("❌ ডিলিট করতে সমস্যা হয়েছে", "danger");
  });
});
