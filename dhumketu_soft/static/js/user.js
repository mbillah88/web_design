function loadModal(modalId, contentId, triggerEl) {
  const url = triggerEl.getAttribute('data-url');
  fetch(url)
    .then(res => res.text())
    .then(html => {
      document.getElementById(contentId).innerHTML = html;
    });
}

function submitRoleForm(event, form) {
  event.preventDefault();
  const formData = new FormData(form);
  fetch(form.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast("Role saved!", true);
      bootstrap.Modal.getInstance(document.getElementById('roleModal')).hide();
      reloadRoleTable();
    } else {
      showToast("Form error!", false);
    }
  });
}

function reloadRoleTable() {
  fetch('/accounts/roles/')
    .then(res => res.text())
    .then(html => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newTable = doc.querySelector('#roleTable');
      if (newTable) {
        document.getElementById('roleTable').innerHTML = newTable.innerHTML;
      }
    });
}

function deleteRole(roleId) {
  fetch(`/accounts/roles/${roleId}/delete/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast("Role deleted!", true);
      reloadRoleTable();
    } else {
      showToast("Delete failed!", false);
    }
  });
}
function togglePermission(roleId, moduleId, btn) {
  fetch("{% url 'toggle_permission' %}", {
    method: 'POST',
    headers: {
      'X-CSRFToken': '{{ csrf_token }}',
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: `role_id=${roleId}&module_id=${moduleId}`
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      btn.classList.toggle('btn-success', data.can_access);
      btn.classList.toggle('btn-secondary', !data.can_access);
      btn.innerText = data.can_access ? '✔' : '✖';
      showToast("Permission updated", true);
    } else {
      showToast("Error: " + data.message, false);
    }
  });
}

//পরয়োজনীয় js user এর জন্য
function loadUserForm(url) {
  fetch(url)
    .then(res => res.text())
    .then(html => {
      document.getElementById('userModalContent').innerHTML = html;
    });
}

function submitUserForm(event, form) {
  event.preventDefault();
  const formData = new FormData(form);
  fetch(form.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(res => {
    if (!res.ok) throw new Error("Network response was not OK");
    return res.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showToast("Saved successfully!", true);
      const modalEl = document.getElementById('userModal');
      const modalInstance = bootstrap.Modal.getInstance(modalEl);
      modalInstance.hide();
      reloadUserTable();
    } else {
      showToast("Form error!", false);
      console.log(data.errors);
    }
  })
  .catch(err => {
    showToast("AJAX error!", false);
    console.error("AJAX catch error:", err);
  });
}

function reloadUserTable() {
  fetch('/accounts/users/')
    .then(res => res.text())
    .then(html => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newTable = doc.querySelector('#userTable');
      if (newTable) {
        document.getElementById('userTable').innerHTML = newTable.innerHTML;
      } else {
        showToast("Reload failed: #userTable not found", false);
      }
    });
}
