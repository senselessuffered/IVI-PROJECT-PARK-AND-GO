(function () {
  var grid = document.getElementById('slotGrid');
  if (!grid) return;

  var summary = document.getElementById('slotSummary');
  var startField = document.querySelector('[name="start_time"]');
  var endField = document.querySelector('[name="end_time"]');
  var dateField = document.querySelector('[name="date"]');
  var spotField = document.querySelector('[name="parking_spot"]');
  var busyUrl = grid.dataset.busyUrl;
  var freeUrl = grid.dataset.freeUrl;
  var excludePk = grid.dataset.excludePk || '';

  function fmt(h) {
    return (h < 10 ? '0' + h : h) + ':00';
  }

  function parseHour(value) {
    var match = /^(\d{1,2}):/.exec(value || '');
    return match ? +match[1] : null;
  }

  function slots() {
    return Array.prototype.slice.call(grid.querySelectorAll('.slot'));
  }

  function slotBy(h) {
    return grid.querySelector('.slot[data-h="' + h + '"]');
  }

  function selectedHours() {
    return slots()
      .filter(function (b) { return b.classList.contains('is-selected'); })
      .map(function (b) { return +b.dataset.h; })
      .sort(function (a, b) { return a - b; });
  }

  function clearSelection() {
    slots().forEach(function (b) { b.classList.remove('is-selected'); });
  }

  function crossesBusy(lo, hi) {
    for (var h = lo; h <= hi; h++) {
      var s = slotBy(h);
      if (s && s.disabled) return true;
    }
    return false;
  }

  function sync() {
    var sel = selectedHours();
    if (!sel.length) {
      if (summary) summary.innerHTML = '<span class="ss-empty">Время не выбрано</span>';
      if (startField) startField.value = '';
      if (endField) endField.value = '';
      return;
    }
    var start = sel[0];
    var end = sel[sel.length - 1] + 1;
    if (summary) summary.textContent = 'Выбрано: ' + fmt(start) + '–' + fmt(end) + ' (' + (end - start) + ' ч)';
    if (startField) startField.value = fmt(start);
    if (endField) endField.value = fmt(end);
  }

  function initFromFields() {
    var start = parseHour(startField && startField.value);
    var end = parseHour(endField && endField.value);
    if (start === null || end === null) return;
    for (var h = start; h < end; h++) {
      var b = slotBy(h);
      if (b && !b.disabled) b.classList.add('is-selected');
    }
  }

  function applyBusy(busy) {
    slots().forEach(function (b) {
      var isBusy = busy.indexOf(+b.dataset.h) !== -1;
      b.classList.toggle('is-busy', isBusy);
      b.disabled = isBusy;
      if (isBusy) b.classList.remove('is-selected');
    });
    sync();
  }

  function refreshBusy() {
    if (!busyUrl) return;
    var day = dateField && dateField.value;
    var spot = spotField && spotField.value;
    if (!day || !spot) {
      applyBusy([]);
      return;
    }
    var url = busyUrl + '?spot=' + encodeURIComponent(spot) + '&date=' + encodeURIComponent(day);
    if (excludePk) url += '&exclude=' + encodeURIComponent(excludePk);
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.ok ? r.json() : { busy: [] }; })
      .then(function (d) { applyBusy(d.busy || []); })
      .catch(function () {});
  }

  function spotOptions() {
    if (!spotField) return [];
    return Array.prototype.slice.call(spotField.options).filter(function (o) { return o.value; });
  }

  function applyFree(free) {
    spotOptions().forEach(function (o) {
      o.disabled = free.indexOf(+o.value) === -1;
    });
    if (spotField.value && free.indexOf(+spotField.value) === -1) {
      spotField.value = '';
      refreshBusy();
    }
  }

  function refreshSpots() {
    if (!freeUrl || !spotField) return;
    var day = dateField && dateField.value;
    var sel = selectedHours();
    if (!day || !sel.length) {
      applyFree(spotOptions().map(function (o) { return +o.value; }));
      return;
    }
    var start = fmt(sel[0]);
    var end = fmt(sel[sel.length - 1] + 1);
    var url = freeUrl + '?date=' + encodeURIComponent(day) +
      '&start=' + encodeURIComponent(start) + '&end=' + encodeURIComponent(end);
    if (excludePk) url += '&exclude=' + encodeURIComponent(excludePk);
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.ok ? r.json() : { free: [] }; })
      .then(function (d) { applyFree(d.free || []); })
      .catch(function () {});
  }

  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('.slot');
    if (!btn || btn.disabled) return;
    var h = +btn.dataset.h;
    if (btn.classList.contains('is-selected')) {
      clearSelection();
    } else {
      var sel = selectedHours();
      if (!sel.length) {
        btn.classList.add('is-selected');
      } else {
        var lo = Math.min(sel[0], h);
        var hi = Math.max(sel[sel.length - 1], h);
        if (crossesBusy(lo, hi)) {
          clearSelection();
          btn.classList.add('is-selected');
        } else {
          for (var x = lo; x <= hi; x++) {
            var s = slotBy(x);
            if (s) s.classList.add('is-selected');
          }
        }
      }
    }
    sync();
    refreshSpots();
  });

  if (dateField) dateField.addEventListener('change', function () {
    refreshBusy();
    refreshSpots();
  });
  if (spotField) spotField.addEventListener('change', refreshBusy);

  initFromFields();
  sync();
})();
