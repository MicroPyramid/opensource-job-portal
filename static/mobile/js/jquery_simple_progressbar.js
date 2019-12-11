(function ( $ ) {
  $.fn.simple_progressbar = function(options) {

    var settings = $.extend({
      normalColor: "#76E29C",
      overflowColor: "#E67373",
      backgroundColor: "#EEEEEE",
      height: '20px',
      width: '200px',
      showValue: false,
      internalPadding: '1px',
      value: undefined,
      valueText: undefined,
    }, options );

    return this.each( function() {
      $_this = $(this); 

      var outer_div, inner_div;
      var updating = false;

      outer_div = $_this.find('.simple-progressbar-generated-div');
      if (outer_div.length == 1) {
        inner_div = outer_div.find('div');
        updating = true;
      } else {
        outer_div = $('<div class="simple-progressbar-generated-div">');
        inner_div = $('<div>');
      }

      var value = settings.value;

      if (typeof(value) == 'undefined') {
        if (updating) {
          value = $_this.data('value');
        } else {
          value = parseFloat($_this.text());
        }
      }

      $_this.data('value', value);

      outer_div.css('background-color', settings.backgroundColor);
      outer_div.css('padding', settings.internalPadding);
      outer_div.css('height', settings.height);
      outer_div.css('width', settings.width);

      inner_div.css('height', '100%');
      inner_div.css('white-space', 'nowrap');
      if (value <= 100) {
        inner_div.css('background-color', settings.normalColor);
        inner_div.css('width', value.toString() + '%');
      } else {
        inner_div.css('background-color', settings.overflowColor);
        inner_div.css('width', '100%');
      }

      if (settings.showValue) {
        if (typeof(settings.valueText) == 'undefined') {
          inner_div.html(value.toString() + "%");
        } else {
          inner_div.html(settings.valueText.toString());
        }
      } else {
        inner_div.html("");
      }
      outer_div.html(inner_div);
      $_this.html(outer_div);

      return this;
    });
  };
}( jQuery ));
