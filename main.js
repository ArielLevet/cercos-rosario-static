// Menú móvil y lightbox para las galerías. Sin dependencias.
(function () {
  'use strict';

  // ---- Menú móvil ----
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  // ---- Lightbox ----
  var links = Array.prototype.slice.call(document.querySelectorAll('a[data-lightbox]'));
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;

  var dlg = document.createElement('dialog');
  dlg.className = 'lightbox';
  dlg.setAttribute('aria-label', 'Galería de imágenes');
  dlg.innerHTML =
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<button class="lb-btn lb-close" type="button" aria-label="Cerrar">&times;</button>' +
    '<button class="lb-btn lb-prev" type="button" aria-label="Anterior">&#8249;</button>' +
    '<button class="lb-btn lb-next" type="button" aria-label="Siguiente">&#8250;</button>';
  document.body.appendChild(dlg);

  var img = dlg.querySelector('img');
  var cap = dlg.querySelector('figcaption');
  var current = 0;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    var thumb = a.querySelector('img');
    img.src = a.getAttribute('href');
    img.alt = thumb ? thumb.alt : '';
    cap.textContent = (current + 1) + ' / ' + links.length + ' — ' + img.alt;
  }

  links.forEach(function (a, i) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      show(i);
      dlg.showModal();
    });
  });

  dlg.querySelector('.lb-close').addEventListener('click', function () { dlg.close(); });
  dlg.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
  dlg.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });

  // Click fuera de la imagen cierra
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });

  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') show(current - 1);
    else if (e.key === 'ArrowRight') show(current + 1);
  });
})();
