document.addEventListener("DOMContentLoaded", function () {
  // 🔹 Password Reset Modal Loader
  document.addEventListener("click", function (e) {
    if (e.target && e.target.id === "passwordResetBtn") {
      e.preventDefault();
      document.getElementById("modalContainer").innerHTML = "";

      fetch("/accounts/password-modal/")
        .then((res) => res.text())
        .then((html) => {
          document.getElementById("modalContainer").innerHTML = html;

          setTimeout(() => {
            const modalEl = document.getElementById("passwordUpdateModal");
            if (modalEl) {
              const oldModal = bootstrap.Modal.getInstance(modalEl);
              if (oldModal) oldModal.hide();
              new bootstrap.Modal(modalEl).show();
            } else {
              window.showToast?.("❌ Modal not found", "danger");
            }
          }, 10);
        });
    }
  });

  // 🔹 Show/Hide Password Toggle
  document.addEventListener("click", function (e) {
    if (e.target?.id === "toggleNewPassword") {
      const input = document.getElementById("newPasswordInput");
      if (input) {
        input.type = input.type === "password" ? "text" : "password";
        e.target.classList.toggle("active");
      }
    }
    if (e.target?.id === "toggleConfirmPassword") {
      const input = document.getElementById("confirmPasswordInput");
      if (input) {
        input.type = input.type === "password" ? "text" : "password";
        e.target.classList.toggle("active");
      }
    }
  });

 document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("submit", function (e) {
    if (e.target && e.target.id === "passwordForm") {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData(form);
      const userId = form.dataset.userId;

      // 🔹 Clear previous errors
      form.querySelectorAll(".is-invalid").forEach((el) => {
        el.classList.remove("is-invalid");
        const feedback = el.nextElementSibling;
        if (feedback && feedback.classList.contains("invalid-feedback")) {
          feedback.classList.remove("d-block");
          feedback.textContent = "";
        }
      });

      // 🔹 Submit via AJAX
      fetch(`/accounts/users/password/${userId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            if (typeof showToast === "function") {
              showToast("✅ পাসওয়ার্ড পরিবর্তন সফল!", "success");
            }
            const modalEl = document.getElementById("passwordUpdateModal");
            if (modalEl) {
              const modalInstance = bootstrap.Modal.getInstance(modalEl);
              if (modalInstance) modalInstance.hide();
            }
          } else if (data.error) {
            Object.entries(data.error).forEach(([field, messages]) => {
              const input = form.querySelector(`[name="${field}"]`);
              if (input) {
                input.classList.add("is-invalid");
                const feedback = input.nextElementSibling;
                if (feedback && feedback.classList.contains("invalid-feedback")) {
                  feedback.classList.add("d-block");
                  feedback.textContent = messages.join(", ");
                }
              }
            });
            if (typeof showToast === "function") {
              showToast("❌ ফর্মে কিছু ভুল আছে", "danger");
            }
          } else {
            if (typeof showToast === "function") {
              showToast("❌ অজানা ত্রুটি", "danger");
            }
          }
        })
        .catch(() => {
          if (typeof showToast === "function") {
            showToast("❌ নেটওয়ার্ক সমস্যা", "danger");
          }
        });
    }
  });
});
});