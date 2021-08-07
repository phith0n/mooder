function submit(action_url) {
    let f = $('<form method="post"></form>');
    const xsrf = $(`{% csrf_token %}`);
    f.append(xsrf);
    f.prop('action', action_url);
    f.appendTo('body').submit();
}
window.onload = function () {
    $(".confirm-alert").on('click', function (e) {
        if(!confirm('确认要执行这个操作？')) {
            return e.preventDefault();
        }
    });
    $("form.form-confirm").on("submit", function (e) {
        if(!confirm('确认要执行这个操作？')) {
            return e.preventDefault();
        }
    });
};