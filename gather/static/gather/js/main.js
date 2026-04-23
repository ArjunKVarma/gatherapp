/**
 * Gather Modern Sharp JS
 * Palette: Royal Blue & Active Green
 */

(function ($) {
  'use strict';

  // 1. Isotope Filtering for Nearby Places
  $(window).on('load', function () {
    if ($('.special-list').length) {
      $('.special-list').imagesLoaded(function() {
        var $grid = $('.special-list').isotope({
          itemSelector: '.special-grid',
          layoutMode: 'fitRows'
        });

        $('.filter-button-group .chip').click(function () {
          $(this).addClass('active').siblings().removeClass('active');
          var filterValue = $(this).attr('data-filter');
          $grid.isotope({ filter: filterValue });
          
          // Trigger AOS refresh after filter
          if (window.AOS) AOS.refresh();
        });
      });
    }
  });

  // 2. Navigation Active States
  const currentPath = window.location.pathname;
  $('.bottom-nav .nav-item, .desktop-nav a').each(function() {
    const linkPath = $(this).attr('href');
    if (linkPath === currentPath) {
      $(this).addClass('active').siblings().removeClass('active');
    }
  });

  // 3. Scroll Header Effect
  $(window).scroll(function() {
    if ($(this).scrollTop() > 30) {
      $('#mainHeader').css({
        'height': '60px',
        'border-bottom-width': '4px'
      });
    } else {
      $('#mainHeader').css({
        'height': '70px',
        'border-bottom-width': '2px'
      });
    }
  });

})(jQuery);

/**
 * OpenStreetMap Nominatim Autocomplete - Refined Sharp Look
 */
(function () {
  'use strict';

  function setupAutocomplete() {
    const input = document.getElementById('address');
    const ginput = document.getElementById('gaddress');
    if (!input) return;

    if (input.dataset.autocompleteBound === 'true') return;
    input.dataset.autocompleteBound = 'true';

    const dropdown = document.createElement('div');
    dropdown.className = 'shadow-lg border-0';
    dropdown.style.cssText = 'position:absolute;z-index:9999;background:#ffffff;border-top:4px solid #28a745;margin-top:5px;padding:0;width:100%;max-height:300px;overflow-y:auto;display:none;box-shadow: 0 15px 35px rgba(0,0,0,0.2) !important;';
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(dropdown);

    let debounceTimer;
    input.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const q = this.value.trim();
      if (q.length < 3) { dropdown.style.display = 'none'; return; }
      
      debounceTimer = setTimeout(() => {
        fetch(`https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=5&q=${encodeURIComponent(q)}`, {
          headers: { 'Accept-Language': 'en' }
        })
        .then(r => r.json())
        .then(results => {
          dropdown.innerHTML = '';
          if (!results.length) { dropdown.style.display = 'none'; return; }
          
          results.forEach(place => {
            const item = document.createElement('div');
            item.className = 'p-3 border-bottom';
            item.style.cssText = 'cursor:pointer;transition:background 0.2s;font-size:14px;color:#172b4d !important;background:#ffffff;';
            item.innerHTML = `<i class="fa fa-location-dot text-primary me-2"></i> <strong style="color:#172b4d !important;">${place.display_name}</strong>`;
            
            item.addEventListener('mouseenter', () => {
              item.style.background = '#e6efff';
              item.style.color = '#0052cc';
            });
            item.addEventListener('mouseleave', () => {
              item.style.background = '#ffffff';
              item.style.color = '#172b4d';
            });
            
            item.addEventListener('mousedown', (e) => {
              e.preventDefault();
              input.value = place.display_name;
              if (ginput) ginput.value = place.display_name;
              dropdown.style.display = 'none';
            });
            dropdown.appendChild(item);
          });
          dropdown.style.display = 'block';
        })
        .catch(() => { dropdown.style.display = 'none'; });
      }, 400);
    });

    input.addEventListener('blur', () => {
      setTimeout(() => { dropdown.style.display = 'none'; }, 200);
    });
  }

  window.checkGaddress = function() {
    const gaddress = document.getElementById('gaddress');
    const address = document.getElementById('address');
    if (gaddress && address && gaddress.value === '' && address.value !== '') {
      gaddress.value = address.value;
    }
    return true;
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAutocomplete);
  } else {
    setupAutocomplete();
  }
})();
