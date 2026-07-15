(function () {
  var buttons = document.querySelectorAll('[data-password-toggle]');
  if (!buttons.length) return;

  buttons.forEach(function (button) {
    var input = document.getElementById(button.getAttribute('data-password-toggle'));
    if (!input) return;

    button.addEventListener('click', function () {
      var isPassword = input.type === 'password';

      input.type = isPassword ? 'text' : 'password';
      button.setAttribute('aria-pressed', isPassword ? 'true' : 'false');
      button.setAttribute('aria-label', isPassword ? 'Скрыть пароль' : 'Показать пароль');
    });
  });
})();
