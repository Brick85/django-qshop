(function($) {
    $(function() {
        if($('body').hasClass('change-form')){
            $('#id_product_type').change(changeType);
            init();
        }
    });

    function changeType(){
        SelectBox.move_all("id_accessories_to", "id_accessories_from");
        SelectFilter.refresh_icons("id_category");
        SelectBox.move_all("id_maps_to", "id_maps_from");
        SelectFilter.refresh_icons("id_maps");
        hideAccessories();
        hideMaps();
    }
    function init(){
        var current = $('#id_product_type').val();
        if(current=='a') hideMaps();
        if(current=='m') hideAccessories();


        $('#producttotypefield_set-group td.field-type_field select').each(function(){
            $(this).before('<span>'+$('option:selected',this).html()+'</span>');
            $(this).hide();
        })

    }

    function hideAccessories(){
        $('.field-accessories').hide();
    }
    function hideMaps(){
        $('.field-maps').hide();
    }

})(django.jQuery);
