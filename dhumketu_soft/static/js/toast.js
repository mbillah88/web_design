function showToast(message, isSuccess = true) {
  const toastEl = document.getElementById('liveToast');
  const toastBody = document.getElementById('toastBody');
  toastBody.innerText = message;
  toastEl.querySelector('.toast-header').classList.toggle('bg-success', isSuccess);
  toastEl.querySelector('.toast-header').classList.toggle('bg-danger', !isSuccess);
  new bootstrap.Toast(toastEl).show();
}
