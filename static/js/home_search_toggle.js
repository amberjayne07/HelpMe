// Joseph Beattie - JQuery for Search Bar Focus on Home.

$(document).ready(function() {
    const $searchInput = $('#search_input');
    const $searchResults = $('#search_results');

    $searchInput.on('focus', function() {
        $searchResults.slideDown(200).removeClass('hidden');
    });

    $searchInput.on('click', function(e) {
        e.stopPropagation();
    });

    $(document).on('click', function(event) {
        if (!$(event.target).closest('.c-command').length) {
            $searchResults.slideUp(200);
        }
    });
});