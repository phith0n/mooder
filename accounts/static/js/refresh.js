$(document).ready(function() {
    $(".captcha").on("click", function() {
        $.getJSON("/captcha/refresh/", function(json) {
            $("#id_captcha_0").val(json.key);
            $(".captcha").attr("src", json.image_url);
        });
    });
});