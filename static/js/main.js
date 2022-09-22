$(document).ready(function (e) {
    // modal for login
    $('.advanced_tag_div').click(function (e) {
        $('#adv_search').plainModal('open');
    });
 

    /* keypad on filter drop */
    $('.filter_drop_down .input_filter').focus(function (e) {
        $('.filter_drop_down').css('position', 'relative')
    });
    /* keypad on filter drop */
    $('.filter_title').click(function () {
        if ($(this).find('span i').hasClass('fa-chevron-down')) {
            $(this).siblings('.filter_options').slideUp('slow');
            $(this).children('span').children('i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
        }
        else {
            $('.fa-chevron-down').parent().parent().next().slideUp('slow');
            $('.fa-chevron-down').removeClass('fa-chevron-down').addClass('fa-chevron-up');
            $(this).siblings('.filter_options').slideDown('slow');
            $(this).children('span').children('i').removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
    });
// filter search starts
    $('li.filter_option').click(function () {
        if ($(this).children('span').hasClass('check_check')) {
            $(this).children('span').removeClass('check_check');
            $(this).addClass('active');
        }
        else {
            $(this).children('span').addClass('check_check');
            $(this).removeClass('active');
        }
    });

    $('form#MailRegisterForm').ajaxForm({
        type: 'POST',
        dataType: 'json',
        data: $('#MailRegisterForm').serialize(),
        url: '/registration/using_email/',
        success: function (data) {
            if (data.error == false) {
                // alert("You are successfully Registered, A verification mail has been sent to Your Mail");
                // alert(data.user_email)
                open_dialog("You are successfully Registered, A verification mail has been sent to Your Mail " + (data.user_email), 'Success!')
                window.location = "/user/reg_success/";
            }
            else if (data['password_error']) {
                $('p.hint').remove();
                $('#mail_password').after('<p class="hint">' + data['password_error'] + '</p>');
            }
            else if (data.response) {
                $('p.hint').remove();
                for (var key in data.response) {
                    $('#mail_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                }
            }
            else {
                $('p.hint').remove();
                $('#mail_response_message').text('');
                $('#mail_response_message').after('<p class="hint">' + data.response_message + '</p>');
            }
        }
    });


    $('.jobseeker_login').click(function (e) {
        e.preventDefault();
        // $('#demo').plainModal('open');
        $('p.hint').remove();
        $('#login_register').modal('show');
        $.post('/jobs/applied_for/', {'job_id': $(this).attr('id')}, function (data) {
        }, 'json')
    })
});

$(".filter_icon").click(function(e){
    e.preventDefault()
    if ($(this).hasClass('collapsed')){
      $(this).children().addClass('glyphicon-minus')
      $(this).children().removeClass('glyphicon-plus')
    }
    else{
      $(this).children().removeClass('glyphicon-minus')
      $(this).children().addClass('glyphicon-plus')
 }
    return
  })

// $(document).on({
//      ajaxStart: function() {
//      $('#login_register').block();
//    },
//      ajaxStop: function() {
//      $('#login_register').unblock()
//    }
// });
 $('input, select').keydown(function () {
    $(this).parent().find('p.hint').remove()
    });

function open_dialog(text, title){
    var myPos = [ $(window).width() / 2, 50 ];
    $('#block_question').text(text);
    $('#block_question').dialog({
        modal: true,
        title: title,
        draggable: false,
        position: myPos,
        buttons: [
            {
                text: "OK",
                click: function () {
                    $(this).dialog("close");
                    $('header').removeClass('fixed')
                    // window.scrollTo(0, 0);
                }
            }
        ]
    });
    $('.ui-dialog-titlebar-close').html('<span>X</span>')
  }


function open_dialog_with_url(text, title, url){
    var myPos = [ $(window).width() / 2, 50 ];
    $('#block_question').text(text);
    // $('.ui-dialog-titlebar-close').empty()
    $('#block_question').dialog({
        modal: true,
        title: title,
        draggable: false,
        position: myPos,
        buttons: [
            {
                text: "OK",
                click: function () {
                    window.location = url;
                }
            }
        ]
    });
    $('.ui-dialog-titlebar-close').html('<span>X</span>')
  }

$('form#ApplicantLoginForm').submit(function(e){
        e.preventDefault();
        register_type = $('#register_type').val()
        if (register_type == 'login'){
            url = '/applicant/login/'
        }else if (register_type == 'forgot_password'){
            url = '/user/forgot_password/'
        }
        else{
            url = '/registration/using_email/'
        }
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: $('#ApplicantLoginForm').serialize(),
            url: url,
            success: function (data) {
                if (data.error == false) {
                    if (register_type == 'register'){
                    window.location = "/user/reg_success/"
                    }
                    else if(register_type == 'forgot_password'){
                    open_dialog_with_url('Sent a link to your email, reset your password by clicking that link',"Success!", '/')
                    }
                    else{
                        window.location = data.redirect_url;
                        }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    for (var key in data.response) {
                        $('#user_login_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                    }
                }
                else {
                    $('p.hint').remove();
                    $('#user_response_message').html('<p class="hint">' + data.response_message + '</p>');
                    // $('#userlogin_response_message').after('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });
    });

$('form#JobMailRegisterForm').submit(function(e){
        e.preventDefault();
        register_type = $('#left_register_type').val()
        if (register_type == 'login'){
            url = '/applicant/login/'
        }else if (register_type == 'forgot_password'){
            url = '/user/forgot_password/'
        }
        else{
            url = '/registration/using_email/'
        }
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: $('#JobMailRegisterForm').serialize(),
            url: url,
            success: function (data) {
                if (data.error == false) {
                    if(register_type == 'forgot_password'){
                    open_dialog_with_url('Password reset Successfull, Check your email for new password',"Success!", '/')
                    }
                    else{
                        window.location = data.redirect_url;
                        }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    for (var key in data.response) {
                        $('#mail_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                    }
                }
                else {
                    $('p.hint').remove();
                    $('#mail_response_message').html('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });

    });
$(".login_modal").click(function(e){
        e.preventDefault()
        $("#login_register").modal('show')
         $("#login_li").addClass('active')
      $("#sign_up_li").removeClass('active')
        $("#modal_head").hide()
         $("#login_div").show()
        $("#register_div").hide()
        $('#user_register_type').val('login')
        $('p.hint').remove();
        $('#button_value').text('Login Here')
        $('#userlogin_password').show()
        $('#pop_up_header').text('Already a Member? Login')
        $('#forgot_pass').show()
    })

    $(".sign_up_li").click(function(){
        $("#login_div").hide()
        $("#register_div").show()
        $("#modal_head").show()
        $('#user_register_type').val('register')
        $('p.hint').remove();
        $()
        $('#button_value').text('Register Now')
        if(applying_for_job == true){
         $('form#ApplicantFormRegister .resume_class').hide()
         $('form#ApplicantFormRegister .help_text').hide()
        }
      })
    $("#login_but").click(function(){
        $("#login_register").modal('show')
         $("#login_li").addClass('active')
        $('#forgot_pass').show()
        $("#modal_head").hide()
         $("#login_div").show()
        $("#register_div").hide()
        $('#user_register_type').val('login')
        $('p.hint').remove();
        $('#button_value').text('Login Here')
        $('#userlogin_password').show()
        $('#pop_up_header').text('Already a Member? Login')
    })
    $(".sign_in_li").click(function(){
      $("#login_li").addClass('active')
      $("#sign_up_li").removeClass('active')
        $("#modal_head").hide()
       $('#pop_up_header').text('Already a Member? Login')
        $('#user_register_type').val('login')
        $('p.hint').remove();
        $('#button_value').text('Login Here')
        $('#userlogin_password').show()
        $('#forgot_pass').show()
    })
    $('#forgot_pass_but').click(function(){
        $('#forgot_pass').hide()
        $("#login_div").show()
        $("#register_div").hide()
        $('#pop_up_header').text('Reset Your Password')
        $('#user_register_type').val('forgot_password')
        $('#userlogin_password').hide()
        $('p.hint').remove();
        $('#button_value').text('SUBMIT')
        $("#modal_head").hide()
    })
    $('#forgot_pass').click(function(){
      $(this).hide();
        $("#modal_head").hide()
      $("#login_li").removeClass('active')
      $("#sign_up_li").removeClass('active')
        $('#pop_up_header').text('Reset Your Password')
        $('#user_register_type').val('forgot_password')
        $('#userlogin_password').hide()
        $('p.hint').remove();
        $('#button_value').text('SUBMIT')
    })
    $('.new_account').click(function(e){
        e.preventDefault();
        $('#login_register').modal('show');
        $("#modal_head").show()
        $('p.hint').remove();
        $('#login_div').hide()
        $('#register_div').show()
        $('#ApplicantFormRegister').get(0).reset()

      });
      $('.new_user_login').click(function(e){
        e.preventDefault();
        $('.login_text').text('Already a Member? Login')
        $("#modal_head").hide()
        $('#register_type').val('login')
        $('.new_user_login').hide()
        $('.new_account').show()
        $('p.hint').remove();
        $('.login_form_button').text('Sign In')
        $('#user_login_password').show()
        $('.forgot_password').show()
      });
      $('.forgot_password').click(function(e){
        e.preventDefault();
        $(this).hide();
        $("#modal_head").hide()
        $('.login_text').text('Reset Your Password')
        $('#register_type').val('forgot_password')
        $('.new_user_login').show()
        $('.new_account').show()
        $('#user_login_password').hide()
        $('p.hint').remove();
        $('.login_form_button').text('SUBMIT')
      });

      $('.left_new_account').click(function(e){
        e.preventDefault();
        $('#login_register').modal('show');
        $("#modal_head").show()
        $("#login_div").hide()
        $("#register_div").show()
        $('#pop_up_header').text('New User? Register Now')
        $('p.hint').remove();
        $('#button_value').text('Register Now')
      });
      $('.left_new_user_login').click(function(e){
        e.preventDefault();
        $('.left_login_text').text('Already a Member? Login')
        $('#left_register_type').val('login')
        $('.left_new_user_login').hide()
        $("#modal_head").hide()
        $('.left_new_account').show()
        $('p.hint').remove();
        $('.left_login_form_button').text('Sign In')
        $('#mail_password').show()
        $('.left_forgot_password').show();
      });
      $('.left_forgot_password').click(function(e){
        e.preventDefault();
        $('.left_forgot_password').hide();
        $('.left_login_text').text('Reset Your Password')
        $('#left_register_type').val('forgot_password')
        $('.left_new_user_login').show()
        $('.left_new_account').hide()
        $('#mail_password').hide()
        $("#modal_head").hide()
        $('p.hint').remove();
        $('.left_login_form_button').text('SUBMIT')
      });

$('form#ApplicantForm').submit(function(e){
        e.preventDefault();
        register_type = $('#user_register_type').val()
        if (register_type == 'login'){
            url = '/applicant/login/'
        }else if (register_type == 'forgot_password'){
            url = '/user/forgot_password/'
        }
        else{
            url = '/registration/using_email/'
        }
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: $(this).serialize(),
            url: url,
            success: function (data) {
                if (data.error == false) {
                    if(register_type == 'forgot_password'){
                    open_dialog_with_url('Password reset Successfull, Check you email for new password',"Success!", '/')
                    }
                    else{
                        window.location = data.redirect_url;
                    }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    $('p.hint').remove();
                    for (var key in data.response) {
                    $('#userlogin_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                    }
                }
                else {
                    $('p.hint').remove();
                    $('#userlogin_response_message').html('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });

    });

$('form#ApplicantFormRegister').submit(function(e){
        e.preventDefault();
        $('.register_form_button').prop('disabled', true);
        $(".register_click").hide()
        $(".load_register").show()
        var formData = new FormData($(this)[0]);
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: formData,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            url: '/registration/using_email/',
            success: function (data) {
                $('.register_form_button').prop('disabled', false);
                if (data.error == false) {
                    if(applying_for_job == true){
                        $("#register_div").hide()
                        $('#candidate_educationform').show()
                        $('#modal_head').text('EDUCATION DETAILS')
                    }
                    else {
                        window.location = data.redirect_url
                    }
                }
                else if (data.response) {
                    $(".register_click").show()
                    $(".load_register").hide()
                    $('p.hint').remove();
                    for (var key in data.response) {
                        if(key == 'technical_skills' ){
                            $('.reg_skill_err').html('<p class="hint">' + data.response[key] + '</p>');
                        }
                        else if(key == 'current_city'){
                          $('.city_err').html('<p class="hint">' + data.response[key] + '</p>');
                        }
                        else{
                            $('#user_register_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                        }
                    }
                }
                else {
                    $('p.hint').remove();
                    $('#user_register_response_message').html('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });

    });

function updating_profile_progress_percantage(profile_value){
      $('#circle').circleProgress({
          value: profile_value/100,
          size: 100,
          startAngle: -Math.PI / 2,
          fill: {gradient: [['#0681c4', .5], ['#4ac5f8', .5]], gradientAngle: Math.PI / 4}
          // fill: {
          //   color: "#fff",
          //   background: "white"
          // }
      });

}
  $('form#resumeupload').submit(function(){
    $(".modal_loading").show()
     var formData = new FormData($(this)[0]);
    $.ajax({
            url: '/upload_resume/',
            type: 'POST',
            dataType: 'json',
            data: formData,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            success: function (data) {
                $(".modal_loading").hide()
                if (data.error == false) {
                    open_dialog_with_url('Resume Uploaded successfully', 'Success', '.')
                } else {
                $("#resume").val('')
                  open_dialog(data.data, 'Info!')
                }
            }
        })
    });

  $('form#uploadresume').submit(function(e){
    e.preventDefault()
    var formData = new FormData($(this)[0]);
    $.ajax({
            url: '/registration/using_email/',
            type: 'POST',
            dataType: 'json',
            data: formData,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            success: function (data) {
                $('#get_resume').val('')
                $('p.hint').remove();
                $(".new_account").click()
                $('#user_register_email').val(data.resume_email)
                $('#user_register_mobile').val(data.resume_mobile)
            }
        })
        });

  // $('#upload_resume_id').click(function (e) {
  //     e.preventDefault()
  //       $('#user_register_resume').click();
  //   });
  // $('#user_register_resume').change(function(){
  //     $('#upload_resume_id').hide()
  //     $('#user_register_resume').show()
  //   })
$(".upload_btn_resume").click(function(e){
    e.preventDefault()
    e.stopPropagation()
    $('#register_from').val('Resume')
    $('#get_resume').click();
})
$('#get_resume').change(function(){
    var clone = $(this).clone();
    clone.attr('id', 'user_register_resume');
    clone.attr('name', 'resume');
    $('.resume_class').html(clone);
    $("#user_register_resume").show()
  $("form#uploadresume").submit()
});

  $('#resume_upload_but').click(function (e) {
  e.preventDefault()
    $('#resume').click();
});
$('#resume').change(function(){
  $("form#resumeupload").submit()
});
$('#job_skills').on("select2:selecting", function(e) {
  $(".skill_err").hide()
  $('p.hint').remove()
});

$('.walkin_block a').click(function (e) {
  e.stopPropagation()
});
$(".walkin_block").click(function(e){
    e.preventDefault()
    window.location = $(this).attr('id')
  })
$('.recruiter_block').click(function(){
    window.location = $(this).attr('id')
})
$('.recruiter_block a').click(function (e) {
  e.stopPropagation()
});

$('.redirect_link').click(function(){
        window.location = $(this).attr('data-href')
      })
$('.add_another').click(function(e){
    $(this).closest('form').submit();
    $(this).addClass('save_other')
})