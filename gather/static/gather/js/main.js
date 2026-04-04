/**
 * Consolidated Main JS for Ruby Travel Manager
 * Cleaned from custom.js | Essential functionality only | jQuery dependent
 */

(function ($) {
  'use strict';

  // Loader (remove preloader if present)
  $(window).on('load', function () {
    $('.preloader, #preloader').fadeOut('slow');
    $('body').css('overflow', 'visible');
  });

  // Fixed Navbar on Scroll
  $(window).on('scroll', function () {
    if ($(this).scrollTop() > 50) {
      $('.main-header').addClass('fixed-menu');
    } else {
      $('.main-header').removeClass('fixed-menu');
    }

    // Back to Top
    if ($(this).scrollTop() > 100) {
      $('#back-to-top').fadeIn();
    } else {
      $('#back-to-top').fadeOut();
    }
  });

  $('#back-to-top').click(function () {
    $('html, body').animate({ scrollTop: 0 }, 600);
    return false;
  });

  // Isotope Filters (Nearby Places)
  $('.container').imagesLoaded(function () {
    var $grid = $('.special-list').isotope({
      itemSelector: '.special-grid'
    });

    $('.special-menu button').click(function () {
      $(this).addClass('active').siblings().removeClass('active');
      var filterValue = $(this).attr('data-filter');
      $grid.isotope({ filter: filterValue });
    });
  });

  // Owl Carousels
  $('.featured-products-box, .events').owlCarousel({
    loop: true,
    margin: 15,
    dots: false,
    autoplay: true,
    autoplayTimeout: 3000,
    autoplayHoverPause: true,
    navText: ["<i class='fas fa-arrow-left'></i>", "<i class='fas fa-arrow-right'></i>"],
    responsive: {
      0: { items: 1, nav: true },
      600: { items: 2, nav: true },
      1000: { items: 3, nav: true }
    }
  });

  // Tooltips
  $('[data-bs-toggle="tooltip"]').tooltip();

  // Slider Range (if used)
  if ($('#slider-range').length) {
    $('#slider-range').slider({
      range: true,
      min: 0,
      max: 4000,
      values: [1000, 3000],
      slide: function (event, ui) {
        $('#amount').val('$' + ui.values[0] + ' - $' + ui.values[1]);
      }
    });
    $('#amount').val('$' + $('#slider-range').slider('values', 0) + ' - $' + $('#slider-range').slider('values', 1));
  }

  // NiceScroll (brand-box if present)
  if ($('.brand-box').length) {
    $('.brand-box').niceScroll({
      cursorcolor: '#9b9b9c'
    });
  }

})(jQuery);

// Google Places autocomplete + form validation
// Used by pages with `#address` (text input) and `#gaddress` (hidden input).
(function () {
  'use strict';

  function setupAutocomplete() {
    if (typeof google === 'undefined' || !google.maps || !google.maps.places) return;

    var input = document.getElementById('address');
    var ginput = document.getElementById('gaddress');
    if (!input || !ginput) return;

    // Avoid double-binding if callback fires more than once.
    if (input.dataset && input.dataset.autocompleteBound === 'true') return;
    if (input.dataset) input.dataset.autocompleteBound = 'true';

    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener('place_changed', function () {
      var place = autocomplete.getPlace();
      if (!place || !place.geometry) {
        input.placeholder = 'Enter a location';
        return;
      }

      // Keep compatibility with existing backend expecting a string.
      input.value = place.name || '';
      ginput.value = place.name || '';

      // If this page has a map container, show a marker.
      var mapEl = document.getElementById('map');
      if (!mapEl) return;

      var location = place.geometry.location;
      var center = { lat: location.lat(), lng: location.lng() };

      var map = new google.maps.Map(mapEl, { center: center, zoom: 15 });
      new google.maps.Marker({ position: center, map: map });
    });
  }

  window.initAutocomplete = function initAutocomplete() {
    // Google callback should run after the API is ready; still guard for DOM state.
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupAutocomplete, { once: true });
      return;
    }
    setupAutocomplete();
  };

  window.checkGaddress = function checkGaddress() {
    var gaddress = document.getElementById('gaddress');
    if (!gaddress) return true; // page does not use the hidden field
    if (gaddress.value === '') {
      alert('Please select a valid option from the autocomplete menu.');
      return false;
    }
    return true;
  };
})();

