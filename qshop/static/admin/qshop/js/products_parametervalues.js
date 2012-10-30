(function($) {
    $(function(){
        if(location.search.indexOf('hide_parameter')!= -1){
            $('.field-parameter').hide();
        }
        $('.vTextField').first().focus();
    });
})(django.jQuery);
