$(document).ready(function() {
    var main_route = (window.location.pathname.split("/")[1]);
    $('.nav-item').removeClass('active');
    $('#nav_' + main_route).addClass('active');
    $(document).on('click', '.nav-item', function (e) {
        $('.nav-item').removeClass('active');
        $('#nav_' + main_route).addClass('active');
    })
})