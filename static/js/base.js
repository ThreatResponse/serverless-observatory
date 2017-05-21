$(document).ready(function(){
    'use strict';

    // Toggle user menu
    $('.menu').click(function() {
        $('.user-menu').toggle();
        $('.menu').toggleClass('enabled');

        // If search-button is visible it's mobile viewport
        if ($('.search-button').is(':visible')) {
            // Make sure search input is hidden
            $('.search-mobile').hide();
            $('.search-button').removeClass('invert');
            // Toggle logo size and menu
            $('.logo-large').toggle();
            $('.logo-small').toggleClass('mui--hidden-xs');
            $('.mui-appbar').toggleClass('menu-enabled');
            $('.search-button').toggleClass('menu-enabled');
        }
    });
    $('.content').click(function() {
        $('.user-menu').hide();
        $('.menu').removeClass('enabled');
    });
    $('.api-key').click(function() {
        $.post( "/api/key", { rotate: true } );
        location.reload();
    });
});
