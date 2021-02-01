if (!window.QApp) {
    window.QApp = {};
}

$.extend(QApp, {
    init: function(){
      AJAX_CONTENT_WRAP = ".j_order-form-wrapper";
      this.initAssignEventsRefreshCart();
    },

    initAssignEventsRefreshCart: function() {
      $(AJAX_CONTENT_WRAP).on("blur", '[name="vat_reg_number"]', function() {
        QApp.ajaxRefreshOrderProducts();
      });

      $(AJAX_CONTENT_WRAP).on("change", '[name="is_delivery"], [name="delivery_type"], [name="country"], [name="delivery_country"], [name="person_type"]', function() {
        QApp.ajaxRefreshOrderProducts();
      });

    },

    ajaxRefreshOrderProducts: function() {
      var event = jQuery.Event("qsop_cart_ajax_updated")
      $.ajax({
          type: "POST",
          url: $('.j_cart_products').data('refresh-url'),
          data: $('.j_order-form').serialize(),
          success: function(data, status) {
            $('.j_order-form-wrapper').html($('.j_order-form-wrapper', data).html());
            $("body").trigger(event);
          }
      });
    }
});

$(function(){
  QApp.init();
});
