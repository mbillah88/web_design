document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('userForm');
  const modalElement = document.getElementById('userModal');
  const modal = new bootstrap.Modal(modalElement);
  const modalTitle = document.getElementById('modalTitle');
  const addUserBtn = document.getElementById('addUserBtn');

  // 🔄 Modal Reset for Add
  addUserBtn?.addEventListener('click', () => {
    form.reset();
    form.setAttribute('data-user-id', '');
    modalTitle.textContent = '➕ নতুন ইউজার';

    form.username.value = '';
    form.email.value = '';
    form.role.selectedIndex = 0;

    ['is_active', 'is_staff', 'is_superuser', 'is_protected'].forEach(name => {
      const checkbox = form.querySelector(`input[name="${name}"]`);
      if (checkbox) checkbox.checked = false;
    });

    ['password', 'confirm_password'].forEach(name => {
      const field = form.querySelector(`input[name="${name}"]`);
      if (field) {
        field.disabled = false;
        field.value = '';
        field.placeholder = name === 'password' ? 'পাসওয়ার্ড' : 'পুনরায় পাসওয়ার্ড';
      }
    });
  });

  // 📝 Modal Fill for Edit
  document.querySelectorAll('.edit-user-btn').forEach(button => {
    button.addEventListener('click', () => {
      const user = JSON.parse(button.getAttribute('data-user'));
      form.setAttribute('data-user-id', user.id);
      modalTitle.textContent = '✏️ ইউজার সম্পাদনা';

      form.username.value = user.username || '';
      form.email.value = user.email || '';
      form.role.value = user.role_id || '';

      form.is_active.checked = user.is_active === 'True';
      form.is_staff.checked = user.is_staff === 'True';
      form.is_superuser.checked = user.is_superuser === 'True';
      form.is_protected.checked = user.is_protected === 'True';

      ['password', 'confirm_password'].forEach(name => {
        const field = form.querySelector(`input[name="${name}"]`);
        if (field) {
          field.value = '';
          field.disabled = true;
          field.placeholder = 'পাসওয়ার্ড পরিবর্তন করতে আলাদা অপশন ব্যবহার করুন';
        }
      });
    });
  });
  form.addEventListener('submit', function(e) {
  e.preventDefault(); // Prevent default form submission

  const formData = new FormData(form);
  const userId = form.getAttribute('data-user-id'); // Set via JS on add/edit
  const url = userId
    ? `/accounts/users/edit/${userId}/`
    : `/accounts/users/create/`;

  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': formData.get('csrfmiddlewaretoken')
    },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast('✅ ইউজার সফলভাবে সংরক্ষণ হয়েছে');
      modal.hide();
      setTimeout(() => location.reload(), 800);
    } else {
      const errorMsg = typeof data.error === 'object'
        ? Object.values(data.error)[0][0]
        : data.error;
      showToast('❌ ' + errorMsg, 'danger');
    }
  })
  .catch(err => {
    console.error('AJAX Error:', err);
    showToast('❌ সংযোগ ব্যর্থ হয়েছে', 'danger');
  });
});

  // 🔔 Toast Feedback
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 mb-2`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    document.getElementById('toastContainer').appendChild(toast);
    new bootstrap.Toast(toast, { delay: 3000 }).show();
  }
});
