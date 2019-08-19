(function ($) {

    $(document).ready(function () {

        $("#registerForm").validate({
            rules: {
                first_name: {
                    required: true,
                    // minLength: 3,
                },
                last_name: {
                    required: true,
                    // minLength: 3,
                },
                email: {
                    required: true,
                    email: true
                },
                username: {
                    required: true,

                },
                password1: {
                    required: true,
                    // minLength: 8
                },
                password2: {
                    equalTo: '#password1'
                },
            },
            messages: {
                email: {
                    required: 'this field is required',
                    email: 'please put valid email '
                },
            }
        });

        $("#loginForm").validate({
            rules: {
                username: {
                    required: true,

                },
                password: {
                    required: true,
                },
            }
        });
    });

})(jQuery);
