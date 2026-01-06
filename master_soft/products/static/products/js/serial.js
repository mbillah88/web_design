function getCSRF() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showToast(msg, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast text-bg-${type} border-0 show mb-2`;
  toast.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto"
      onclick="this.parentElement.parentElement.remove()"></button></div>`;
  document.getElementById('toastContainer').appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

function clearSerialForm() {
  document.getElementById("serialForm").reset();
  document.getElementById("serialId").value = "";
  document.getElementById("deleteSerialBtn").classList.add("d-none");
}

function fillSerialForm(data) {
  document.getElementById("serialId").value = data.id;
  document.getElementById("serialNumber").value = data.serial_number;
  document.getElementById("deleteSerialBtn").classList.remove("d-none");
}

document.getElementById("serialForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const id = document.getElementById("serialId").value;
  const url = id ? `/serial/${id}/edit/` : `/serial/create/`;

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRF(),
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams(new FormData(this))
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("serialModal")).hide();
      clearSerialForm();
      loadSerialList();
    } else {
      showToast(data.error, "danger");
    }
  });
});

document.getElementById("deleteSerialBtn").addEventListener("click", function () {
  const id = document.getElementById("serialId").value;
  if (!confirm("❗ আপনি কি নিশ্চিতভাবে সিরিয়ালটি মুছে ফেলতে চান?")) return;

  fetch(`/serial/${id}/delete/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF() }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message);
      bootstrap.Modal.getInstance(document.getElementById("serialModal")).hide();
      clearSerialForm();
      loadSerialList();
    } else {
      showToast(data.error, "danger");
    }
  });
});

function loadSerialList() {
  fetch(`/products/product/{{ product.id }}/serial/list-json/`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("serialTableBody");
      tbody.innerHTML = "";
      data.data.forEach(s => {
        tbody.innerHTML += `
          <tr>
            <td>${s.serial_number}</td>
            <td><span class="badge bg-${s.is_sold ? 'danger' : 'success'}">${s.is_sold ? 'বিক্রি হয়েছে' : 'স্টকে'}</span></td>
            <td>${s.warranty_expiry || 'N/A'}</td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteSerial(${s.id})">🗑️</button></td>
          </tr>
        `;
      });
    });
}

document.addEventListener("DOMContentLoaded", loadSerialList);
