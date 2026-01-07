function getCSRF() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast text-bg-${type} border-0 show mb-2`;
  toast.innerHTML = `<div class="d-flex">
    <div class="toast-body">${message}</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto"
      onclick="this.parentElement.parentElement.remove()"></button>
  </div>`;
  document.getElementById('toastContainer').appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

function clearCategoryForm() {
  document.getElementById("categoryForm").reset();
  document.getElementById("categoryId").value = "";
  document.getElementById("deleteCategoryBtn").classList.add("d-none");
}

document.getElementById("categoryForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const catId = document.getElementById("categoryId").value;
  const url = catId
    ? `/products/category/${catId}/edit/`
    : `/products/category/create/`;

  const formData = new FormData(this); // ✅ Correct way

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRF()
      // ✅ Don't set Content-Type manually
    },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("categoryModal")).hide();
      clearCategoryForm();
      location.reload();
    } else {
      showToast(`❌ ${data.error}`, "danger");
    }
  });
});


document.querySelectorAll(".edit-category-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const catId = this.dataset.id;

    fetch(`/products/category/${catId}/json/`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          fillCategoryForm(data.category);
          bootstrap.Modal.getOrCreateInstance(document.getElementById("categoryModal")).show();
        } else {
          showToast(`❌ ${data.error}`, "danger");
        }
      });
  });
});


document.querySelectorAll(".delete-category-btn").forEach(btn => {
  btn.addEventListener("click", function () {
    const catId = this.dataset.id;
    const catName = this.dataset.name;

    if (!confirm(`❗ আপনি কি '${catName}' ক্যাটাগরি মুছে ফেলতে চান?`)) return;

    fetch(`/products/category/${catId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCSRF() }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message);
        location.reload();
      } else {
        showToast(`❌ ${data.error}`, "danger");
      }
    });
  });
});
function previewImage(inputId, previewId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  input.addEventListener("change", function () {
    const file = this.files[0];
    if (file && file.type.startsWith("image/") && file.size < 2 * 1024 * 1024) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.classList.remove("d-none");
      };
      reader.readAsDataURL(file);
    } else {
      preview.src = "#";
      preview.classList.add("d-none");
      showToast("❌ ফাইলটি ইমেজ হতে হবে এবং 2MB এর কম হতে হবে", "danger");
      input.value = "";
    }
  });
}

previewImage("categoryIcon", "iconPreview");
previewImage("categoryBanner", "bannerPreview");

function clearCategoryForm() {
  document.getElementById("categoryForm").reset();
  document.getElementById("categoryId").value = "";
  document.getElementById("deleteCategoryBtn").classList.add("d-none");
  document.getElementById("iconPreview").classList.add("d-none");
  document.getElementById("bannerPreview").classList.add("d-none");
}

function fillCategoryForm(cat) {
  document.getElementById("categoryId").value = cat.id;
  document.getElementById("categoryName").value = cat.name;
  document.getElementById("categoryParent").value = cat.parent_id || "";
  document.getElementById("categoryDescription").value = cat.description || "";
  document.getElementById("categoryActive").value = cat.is_active ? "true" : "false";

  if (cat.icon_url) {
    document.getElementById("iconPreview").src = cat.icon_url;
    document.getElementById("iconPreview").classList.remove("d-none");
  }

  if (cat.banner_url) {
    document.getElementById("bannerPreview").src = cat.banner_url;
    document.getElementById("bannerPreview").classList.remove("d-none");
  }

  document.getElementById("deleteCategoryBtn").classList.remove("d-none");
}
