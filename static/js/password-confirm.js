(function () {
  var form = document.querySelector('form[data-password-confirm]');
  if (!form) return;

  var password = form.querySelector('[name$="password1"]');
  var confirm = form.querySelector('[name$="password2"]');
  if (!password || !confirm) return;

  function check() {
    if (confirm.value && confirm.value !== password.value) {
      confirm.setCustomValidity('Пароли не совпадают');
    } else {
      confirm.setCustomValidity('');
    }
  }

  password.addEventListener('input', check);
  confirm.addEventListener('input', check);
})();
