
(function ($) {

    $(document).ready(function () {

        $(this).on('focus', '[data-toggle="datepicker"]', function () {
            $(this).datepicker({
                language: 'en-US',
                format: 'dd-mm-yyyy',
                autoHide: true,
                zIndex: 2048
            });
        });
        
        $(".chosen-select").chosen();


    });


})(jQuery);


