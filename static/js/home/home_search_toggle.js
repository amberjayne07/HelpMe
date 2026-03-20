// Joseph Beattie - JQuery for Search Bar Focus on Home, heavily updated with ajax to work with input and results.

$(document).ready(function() {
    $.ajaxSetup({
        headers: { "X-Requested-With": "XMLHttpRequest" }
    });

    const $searchInput = $('#search_input');
    const $searchResults = $('#search_results');
    let debounceTimer;

    function openSearch() {
        $searchResults.removeClass('opacity-0 translate-y-2 pointer-events-none')
                      .addClass('opacity-100 translate-y-0 pointer-events-auto');
    }

    function closeSearch() {
        $searchResults.addClass('opacity-0 translate-y-2 pointer-events-none')
                      .removeClass('opacity-100 translate-y-0 pointer-events-auto');
    }

    $searchInput.on('input', function() {
        const query = $(this).val().trim();

        clearTimeout(debounceTimer);

        if (query.length === 0) {
            closeSearch();
            return;
        }

        debounceTimer = setTimeout(function() {
            if (query.length > 1) {
                $.ajax({
                    url: '/search/',
                    method: 'GET',
                    data: { 'q': query },
                    success: function(data) {
                        $searchResults.find('.bg-white').html(data);
                    }
                });
            }
        }, 250);
    });

    $searchInput.on('focus click', function(e) {
        e.stopPropagation();
        openSearch();
    });

    $(document).on('click', function(event) {
        if (!$(event.target).closest('.max-w-\[700px\]').length) {
            closeSearch();
        }
    });

    $(document).on('keydown', function(e) {
        const isTyping = $('input, textarea, [contenteditable="true"]').is(':focus');
        if (e.which === 191 && !isTyping) {
            e.preventDefault();
            $searchInput.focus();
            openSearch();
        }
        if (e.which === 27) {
            closeSearch();
            $searchInput.blur();
        }
    });
});