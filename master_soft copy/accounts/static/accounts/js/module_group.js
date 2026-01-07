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
  setTimeout(() => toast.remove(), 4000);
}

function clearGroupForm() {
  document.getElementById("groupForm").reset();
  document.getElementById("groupId").value = "";
}

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('groupManagerModal');
  const form = document.getElementById('groupForm');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const data = new URLSearchParams(new FormData(form));
    fetch("/accounts/module-groups/save/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRF(),
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: data
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(`✅ Group "${data.group.name}" ${data.created ? 'added' : 'updated'} successfully`);
        bootstrap.Modal.getInstance(modal).hide();
        clearGroupForm();
        location.reload();
      } else {
        showToast(`❌ ${data.error}`, "danger");
      }
    })
    .catch(err => showToast("❌ Server error", "danger"));
  });

  document.querySelectorAll(".edit-group-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const data = JSON.parse(btn.getAttribute("data-group"));
      document.getElementById("groupId").value = data.id;
      document.getElementById("groupName").value = data.name;
      document.getElementById("groupIcon").value = data.icon;
      document.getElementById("groupOrder").value = data.order;
    });
  });

  document.querySelectorAll(".delete-group-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      const name = btn.dataset.name;
      if (!confirm(`⚠️ Are you sure you want to delete group "${name}"?`)) return;

      fetch(`/accounts/module-groups/delete/${id}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRF() }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(data.message);
          document.getElementById(`groupRow${id}`)?.remove();
        } else {
          showToast(`❌ ${data.error}`, "danger");
        }
      })
      .catch(err => showToast("❌ Server error", "danger"));
    });
  });
});
