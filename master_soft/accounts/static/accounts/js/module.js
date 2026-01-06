//Sync Btn...
    function syncModules(url, onSuccess = null, onError = null) {
      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(`✅ Sync complete: ${data.added} new module${data.added !== 1 ? "s" : ""} added`, "success");
          if (typeof onSuccess === "function") onSuccess(data);
        } else {
          showToast(`❌ Sync failed: ${data.error || "Unknown error"}`, "danger");
          if (typeof onError === "function") onError(data);
        }
      })
      .catch(err => {
        showToast("❌ Server error during sync", "danger");
        if (typeof onError === "function") onError(err);
      });
    }

    document.getElementById("syncModulesBtn").addEventListener("click", function () {
      const url = this.dataset.url;
      syncModules(url, function (data) {
        console.log("✅ Sync complete:", data);
        // Optional: reload table or update UI
      });
    });
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }



    // Open modal for new module
    document.getElementById('addModuleBtn').addEventListener('click', () => {
      const form = document.getElementById('moduleForm');
      form.reset();
      document.getElementById('moduleId').value = '';
      document.getElementById('iconPreview').className = 'fs-4 text-primary';
      document.getElementById('moduleModalLabel').innerText = '➕ New Module';

    });

    // Open modal for editing module
    document.querySelectorAll('.edit-module-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        try {
          const form = document.getElementById('moduleForm');
          form.reset(); // ✅ Clear previous data

          const data = JSON.parse(btn.getAttribute('data-module'));

          // ✅ Populate new data
          document.getElementById('moduleId').value = data.id || '';
          document.getElementById('moduleName').value = data.name || '';
          document.getElementById('moduleLabel').value = data.label || '';
          document.getElementById('moduleUrl').value = data.url_name || '';
          document.getElementById('moduleIcon').value = data.icon || '';
          document.getElementById('moduleOrder').value = data.order || 0;
          document.getElementById('moduleParent').value = data.parent_id || '';
          document.getElementById('moduleGroup').value = data.group_id || '';
          document.getElementById('moduleVisible').checked = data.is_visible ?? true;
          document.getElementById('moduleHeader').checked = data.is_header ?? false;

          // ✅ Update icon preview
          document.getElementById('iconPreview').className = (data.icon || '') + ' fs-4 text-primary';

          // ✅ Update modal title
          document.getElementById('moduleModalLabel').innerText = '✏️ মডিউল সম্পাদনা';
        } catch (err) {
          alert('❌ ডাটা লোড করতে সমস্যা হয়েছে');
          console.error(err);
        }
      });
    });
    document.getElementById('moduleForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const form = e.target;
      const data = new URLSearchParams(new FormData(form));
      const moduleId = document.getElementById('moduleId').value;
      const url = moduleId
        ? `/accounts/modules/form/${moduleId}/`
        : `/accounts/modules/form/`;

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: data
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert(`✅ মডিউল "${data.module.name}" ${data.created ? 'যোগ' : 'আপডেট'} হয়েছে`);
          form.reset();
          bootstrap.Modal.getInstance(document.getElementById('moduleModal')).hide();
          location.reload(); // অথবা dynamic row update
        } else {
          alert("❌ ফর্ম সমস্যা:\n" + Object.values(data.error).map(e => e[0].message).join('\n'));
        }
      })
      .catch(err => alert("❌ সার্ভার সমস্যা: " + err));
    });
    
    function extractErrors(errorObj) {
      const errors = [];

      for (const field in errorObj) {
        const fieldErrors = errorObj[field];
        if (Array.isArray(fieldErrors)) {
          fieldErrors.forEach(err => {
            errors.push(typeof err === 'string' ? err : err.message || JSON.stringify(err));
          });
        } else {
          errors.push(typeof fieldErrors === 'string' ? fieldErrors : JSON.stringify(fieldErrors));
        }
      }

      return errors;
    }

    // Live icon preview
    document.getElementById('moduleIcon').addEventListener('input', e => {
      document.getElementById('iconPreview').className = e.target.value + ' fs-4 text-primary';
    });

    // Open icon picker modal
    document.getElementById('openIconPicker').addEventListener('click', () => {
      const iconModal = new bootstrap.Modal(document.getElementById('iconPickerModal'), {
        backdrop: 'static',
        keyboard: false
      });
      iconModal.show();
    });

    // Select icon from picker
    document.querySelectorAll('.icon-select-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const selectedIcon = btn.getAttribute('data-icon');
        document.getElementById('moduleIcon').value = selectedIcon;
        document.getElementById('iconPreview').className = selectedIcon + ' fs-4 text-primary';
        bootstrap.Modal.getInstance(document.getElementById('iconPickerModal')).hide();
      });
    });
    