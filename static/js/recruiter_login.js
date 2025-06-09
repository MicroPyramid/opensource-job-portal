// $.fn.modal.Constructor.prototype.enforceFocus = function() {};
$("select#user_register_technical_skills").select2({ placeholder: "Choose required Skillset", maximumSelectionSize: 6 });
$("select#user_register_current_city").select2({ placeholder: "Choose current location", 'positionDropdown': true })
$(window).scroll(function () {
  if ($(this).scrollTop() > 1) {
    $('header').addClass("sticky");
  }
  else {
    $('header').removeClass("sticky");
  }
  var sticky = $('.sticky'),
    scroll = $(window).scrollTop();

  if (scroll >= 80) sticky.addClass('fixed');
  else sticky.removeClass('fixed');
});
$(document).ready(function () {
  $(".customGPlusSignIn").click(function (e) {
    window.location = $(this).attr('data-href')
  })
  $(".common_authentic_form").hide();
  $(".login_form").show();
  $(".register_form").show();
  $("#register-client_type").attr('checked', 'checked');
  $(".show_form").click(function () {
    $(".common_authentic_form").hide();
    $(".register_form").show();
    $('div.error').remove();
    $('.form-control').val('');
    $("#register-client_type").attr('checked', 'checked');
    $('.company').hide();
    var target = $(this).attr("class").split(" ")[0];
    $("." + target).show();
  });
  $('form#frm_forgot').submit(function (e) {
    e.preventDefault();
    $.post("/recruiter/pwdreset/", $('form#frm_forgot').serialize(), function (data) {
      $('div.error').remove();
      if (data.error == false) {
        open_dialog_with_url(data.info, 'Info!!', '.')
      } else {
        $('#forgot-email').after('<div class="error">' + data.email + '</div>');
      }
    }, 'json');
  });

  $('form#reg-form').submit(function (e) {
    e.preventDefault();
    console.log('Form submission triggered');
    console.log('Form data:', $("form#reg-form").serialize());

    $.post("/recruiter/login/", $("form#reg-form").serialize(), function (data) {
      console.log('Response received:', data);
      if (data.error) {
        $('div.error').remove();
        console.log(data.captcha_response)
        if (data.captcha_response) {
          $('.captcha').after('<div class="error">' + data.captcha_response + '</div>');
        }
        for (var key in data.message) {
          $('#register-' + key).after('<div class="error">' + data.message[key] + '</div>');
        }
      } else {
          window.location = "/recruiter/profile/";
      }
    }, 'json').fail(function (xhr, status, error) {
      console.log('AJAX request failed:', status, error);
      console.log('Response text:', xhr.responseText);
    });
  })

  $("#frm_login").submit(function (e) {
    e.preventDefault();
    //$('#msg').css('display', 'block');
    //$('#msg').html('Authenticating...');
    $.post("/post-job/", $("#frm_login").serialize(), function (msg) {
      if (msg.error == false) {
        if (msg.is_login) {
          if (msg.is_company_recruiter) {
            window.location = "/recruiter/mobile/verify/";
          }
          else {
            window.location = "/agency/mobile/verify/";
          }
        }
        else {
          window.location = msg.redirect_url
        }
      }
      else {
        $('.error_message').html(msg.message)
        $('#demo').plainModal('open');
        //$('#msg').html(msg.message);
        //$('#msg').css('color', 'red');
        //setTimeout('$("#msg").fadeOut("slow")', 5000);
      }
    }, 'json');
  });
  $('.menu_wrap .dropdown-menu').hide();
  $(".dropdown").hover(
    function (e) {
      e.preventDefault();
      $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideDown("400");
      $(this).toggleClass('open');
    },
    function (e) {
      e.preventDefault();
      $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideUp("400");
      $(this).toggleClass('open');
    }
  );
});
$(document).ready(function (e) {
  $('.client_type').click(function (e) {
    $('div.error').remove();
    if ($(this).val() == 'recruiter') {
      $('.company').hide();
      $('#register-name').val('')
      $('#register-website').val('')
    }
    else {
      $('.company').show();
    }
  })

});
$("#okbutton").click(function (e) {
  $('#demo').plainModal('close');
})


$('.latest-jobs').click(function (e) {
  window.location = '/jobs/';
});
$("#other_location").click(function (e) {
  $(this).parent().find('.hint').remove()
  if ($(this).is(":checked")) {
    $(this).parent().find('.select2').hide()
    $("#user_register_other_location").show()
  }
  else {
    $(this).parent().find('.select2').show()
    $("#user_register_other_location").hide()
  }
})