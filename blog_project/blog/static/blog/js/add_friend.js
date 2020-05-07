$(document).ready(
    function() {
        const input = $("#input_id");
        const search_button = $("#search_button_id");
        search_button.click(function() {
            $(location).attr('href', '?username=' + input.val())
        });
    }
)
