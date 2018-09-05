if (!window.QApp) {
    window.QApp = {};
}

$.extend(QApp, {
    init: function(){
      LEGAL_FIELDS_WRAP = ".j_legal_fields";
      DELIVERY_FIELDS_WRAP = ".j_delivery_fields";
      HIDE_CLASS = "block-hide";

      DELIVER_COUNTRY_FIELD = $('[name="delivery_country"]');
      TOGGLE_SCOPE = $('[name="delivery_country"]').data('toggle-scope');
      TOGGLE_TEMPLATE = $('[name="delivery_country"]').data('toggle-template');

      this.initPersonTypeChoose();
      this.initIsDeliveryChoose();
      this.initDeliveryCountryChoose();
      this.assignEventsRefreshCart();
    },

    initDeliveryCountryChoose: function() {
      QApp.deliveryCountryChoose( DELIVER_COUNTRY_FIELD.find(':selected') );
      DELIVER_COUNTRY_FIELD.change(function() {
        QApp.deliveryCountryChoose( $(this).children('option:selected') );
        // QApp.ajaxRefreshOrderProducts();
      });
    },

    deliveryCountryChoose: function(allowed_countries) {
      $(TOGGLE_TEMPLATE, TOGGLE_SCOPE).hide();

      if(allowed_countries.data('countries-pks') == undefined)
        return;

      allowed_countries = allowed_countries.data('countries-pks').toString().split(',');

      $.each(allowed_countries, function( index, value ) {
        $(TOGGLE_TEMPLATE + value, TOGGLE_SCOPE).show();
      });

    },

    assignEventsRefreshCart: function() {


      $( '[name="vat_reg_number"]' ).blur(function() {
        QApp.ajaxRefreshOrderProducts();
      });

      $('[name="delivery_type"], [name="country"]').add(DELIVER_COUNTRY_FIELD).change(function() {
        QApp.ajaxRefreshOrderProducts();
      });
    },

    ajaxRefreshOrderProducts: function() {
      $.ajax({
          type: "POST",
          url: $('.j_cart_products').data('refresh-url'),
          data: $('.j_order-form').serialize(),
          // beforeSend: function() {
              // console.log( 'before send' );
          // },

          success: function(data, status) {
              $('.j_cart_products').html($('.j_cart_products', data).html());

          },
          // error: function(data){
              // console.log('hellooo - this is an error!!!');
          // }
      });
    },

    initPersonTypeChoose: function() {
      $(':radio[name="person_type"]').change(function() {
        QApp.showHideBlock(LEGAL_FIELDS_WRAP, $(this).val(), 0);
      });
    },

    initIsDeliveryChoose: function() {
      $(':radio[name="is_delivery"]').change(function() {
        QApp.showHideBlock(DELIVERY_FIELDS_WRAP, $(this).val(), 0);
      });
    },

    showHideBlock: function(fields_wrap, selected_val, hide_if) {
      if(selected_val == hide_if) $(fields_wrap).addClass(HIDE_CLASS);
      else $(fields_wrap).removeClass(HIDE_CLASS);
    }

});

$(function(){
  QApp.init();
});
