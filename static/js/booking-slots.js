(function () {
  var grid = document.getElementById('slotGrid');
  if (!grid) return;

  var summary = document.getElementById('slotSummary');
  var startField = document.querySelector('[name="start_time"]');
  var endField = document.querySelector('[name="end_time"]');

  function fmt(h) {
    return (h < 10 ? '0' + h : h) + ':00';
  }

  function parseHour(value) {
    var match = /^(\d{1,2}):/.exec(value || '');
    return match ? +match[1] : null;
  }

  function initFromFields() {
    var start = parseHour(startField && startField.value);
    var end = parseHour(endField && endField.value);
    if (start === null || end === null) return;
    for (var h = start; h < end; h++) {
      var btn = grid.querySelector('.slot[data-h="' + h + '"]');
      if (btn && !btn.disabled) btn.classList.add('is-selected');
    }
  }

  function update() {
    var selected = Array.prototype.slice
      .call(grid.querySelectorAll('.slot.is-selected'))
      .map(function (b) { return +b.dataset.h; })
      .sort(function (a, b) { return a - b; });

    if (!selected.length) {
      if (summary) summary.innerHTML = '<span class="ss-empty">Время не выбрано</span>';
      if (startField) startField.value = '';
      if (endField) endField.value = '';
      return;
    }

    var start = selected[0];
    var end = selected[selected.length - 1] + 1;
    if (summary) summary.textContent = 'Выбрано: ' + fmt(start) + '–' + fmt(end) + ' (' + selected.length + ' ч)';
    if (startField) startField.value = fmt(start);
    if (endField) endField.value = fmt(end);
  }

  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('.slot');
    if (!btn || btn.disabled) return;
    btn.classList.toggle('is-selected');
    update();
  });

  initFromFields();
  update();
})();
