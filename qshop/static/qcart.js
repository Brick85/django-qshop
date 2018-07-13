if (!window.QApp) {
    window.QApp = {};
}

$.extend(QApp, {
    init: function(){
      LEGAL_FIELDS_WRAP = ".j_legal_fields";
      DELIVERY_FIELDS_WRAP = ".j_delivery_fields";
      HIDE_CLASS = "block-hide";
      this.initPersonTypeChoose();
      this.initIsDeliveryChoose();
      this.initDeliveryCountryChoose();
    },

    initDeliveryCountryChoose: function() {
      $('[name="delivery_country"]').change(function() {
        console.log('check');
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
