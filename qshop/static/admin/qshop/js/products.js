(function($) {
    $(function() {
        $('#producttoparameter_set-group a.add-related').each(function(){
            id = $('.field-parameter select', $(this).closest('tr')).val();
            this.href += (this.href.indexOf('?')!= -1 ? '&' : '?') + 'parameter=' + id + '&hide_parameter';
        });

        $('#producttoparameter_set-group a.change-related').each(function(){
            id = $('.field-parameter select', $(this).closest('tr')).val();
            href_template = $(this).data('href-template');
            href = $(this).attr('href');


            $(this).attr('data-href-template', href_template + (href_template.indexOf('?')!= -1 ? '&' : '?') + 'parameter=' + id + '&hide_parameter');

            if(href)
                $(this).attr('href', href + (href.indexOf('?')!= -1 ? '&' : '?') + 'parameter=' + id + '&hide_parameter');

        });


    });

})(django.jQuery);
