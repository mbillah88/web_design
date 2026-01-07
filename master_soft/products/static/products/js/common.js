function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast text-bg-${type} border-0 show mb-2`;
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  document.getElementById("toastContainer").appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function refreshDropdown(id, name, dropdownId) {
  const dropdown = document.getElementById(dropdownId);
  const option = document.createElement("option");
  option.value = id;
  option.textContent = name;
  dropdown.appendChild(option);
  dropdown.value = id;
}
