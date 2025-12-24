/* menu */
$('.menu').click(function(e){
	$('.filter_drop_down').slideUp(400);
	$('.sign_in_drop').slideUp(400);
	$('.login_pop_up').hide();
	if($('.vertical_menu').css('display') == 'block'){
		//alert('yes');
		//$('.logo_title').hide();
		$('.overlay_div').hide();
		//$('.vertical_menu').slideUp(400);
		$('.vertical_menu').animate({
		  left: '-400px'
		 }, 600,function(){
		 	$('.vertical_menu').hide();
		 });

	}
	else{
		//alert('no');
		$('.overlay_div').show();
		//$('.logo_title').show();
		//$('.vertical_menu').slideDown(400);
		$('.vertical_menu').show().animate({
		  left: '0px'
		 }, 600);

	}
});
$('body .overlay_div').click(function(e){
	reset_menu();
})
/* menu */
/* filter */
$('.filter_icon').click(function(e){
	e.stopPropagation();
	if($('.filter_drop_down').is(':visible')==true){
		$('.overlay_div').hide()
		$('.filter_drop_down').slideUp(400);
	}
	else{
		reset_menu();
		$('.overlay_div').show()
		$('.filter_drop_down').slideDown(400);
	}
});
$('.filter_drop_down').click(function(e){
	e.stopPropagation();
})
/* filter */
/* sign in */
$('.sign_in_icon').click(function(e){
	e.stopPropagation();
	if($('.sign_in_drop').is(':visible')==true){
		$('.overlay_div').hide()
		$('.sign_in_drop').slideUp(400);
	}
	else{
		reset_menu();
		$('.overlay_div').show()
		$('.sign_in_drop').slideDown(400);
	}
})


/* sign in*/
/* menu reset */
function reset_menu(){
	/*console.log('reset')*/
	$('.overlay_div').hide();
	$('.vertical_menu').hide();
	$('.filter_drop_down').slideUp(400);
	$('.sign_in_drop').slideUp(400);
	$('.login_pop_up').hide()
	$('.share_pop_up').hide()
    $('.login_pop_up').hide()
	$('.create_similarjob_alert').hide()
}
/* menu reset */
/* job_list */
$('#job_list .close_icon').click(function(e){
    e.preventDefault();
	e.stopPropagation();
	$(this).parent().fadeOut('slow');
})
/* job_list*/

/* login job seeker login */
$('.job_seeker').click(function(e){
	e.preventDefault();
	e.stopPropagation();
	reset_menu();
	$('.overlay_div').show();
	$('.login_pop_up').show('fast');
})
$('.login_reg_pop').click(function(e){
	e.preventDefault();
	e.stopPropagation();
	reset_menu();
  $('#ApplicantForm').trigger("reset");
  $("#sign_in_li").click()
  $('p.hint').remove()
	$('.overlay_div').show();
	$('.login_pop_up').show('fast');
})
$(".reg_pop_up").click(function(){
    reset_menu();
  $('#ApplicantForm').trigger("reset");
  $("#sign_up_li").click()
  $('p.hint').remove()
    $('.overlay_div').show();
    $('.login_pop_up').show('fast');
})
$('.share_jobspost').click(function(e){
	e.preventDefault();
	e.stopPropagation();
	reset_menu();
	$('.overlay_div').show();
	$('.share_pop_up').show('fast');
})
$('.close_pop_up').click(function(e){
	reset_menu();
})
/* login job seeker login */
/* keypad on filter drop */
$('.filter_drop_down .input_filter').focus(function(e){
       $('.filter_drop_down').css('position','relative')
});
/* keypad on filter drop */


        $("#sign_up_li").click(function () {
            $("#login_div").hide()
            $("#register_div").show()
            // $(this).hide()
            // $("#sign_in_li").show()
            $('#user_register_type').val('register')
            $('p.hint').remove();
            // $("#forgot_pass").show()
            // $('#modal-header').text("New User? Register Now")
            // $('#button_value').text('Register Now')
            // $('#userlogin_password').show()

        })
        $("#sign_in_li").click(function () {
            $("#register_div").hide()
            $("#login_div").show()
            $(this).hide()
            $("#sign_up_li").show()
            $('#user_register_type').val('login')
            $('p.hint').remove();
            $('#modal-header').text("Already a Member? Login")
            $('#button_value').text('LOGIN')
            $("#forgot_pass").show()
            $('#userlogin_password').show()

        })
     $("#sign_in_but").click(function () {
            $("#sign_in_li").hide()
            $("#register_div").hide()
            $("#login_div").show()
            $('#user_register_type').val('login')
            $('p.hint').remove();
            $('#modal-header').text("Already a Member? Login")
            $('#button_value').text('LOGIN')
            $("#forgot_pass").show()
            $('#userlogin_password').show()

        })
        $("#forgot_pass").click(function () {
            $(this).hide()
            $('#sign_in_li').show()
            $('#sign_up_li').show()
            $('#modal-header').text("Reset Your Password")
            $('#button_value').text('SUBMIT')
            $('p.hint').remove();
            $('#user_register_type').val('forgot_password')
            $('#userlogin_password').hide()

        })

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
            data: $('#ApplicantForm').serialize(),
            url: url,
            success: function (data) {
                if (data.error == false) {
                  if(data.redirect_url){
                    window.location = data.redirect_url;
                  }
                  else{
                    open_dialog("Password Has been sent to your email address", 'Success!')
                      reset_menu();
                  }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    for (var key in data.response) {
                    $('#userlogin_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                    }
                }
                else {
                    $('p.hint').remove();
                    $('#userlogin_response_message').html('<p class="hint">' + data.response_message + '</p>');
                    // $('#userlogin_response_message').after('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });

    });
$('form#ApplicantFormRegister').submit(function(e){
        e.preventDefault();
        $('.login_form_button').prop('disabled', true);
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
                $('.login_form_button').prop('disabled', false);
                if (data.error == false) {
                    $('p.hint').remove();
                  if(data.redirect_url){
                    window.location = data.redirect_url;
                  }
                  else{
                   window.location= '.'
                  }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    for (var key in data.response) {
                        if(key == 'technical_skills' ){
                  $('.reg_skill_err').html('<p class="hint">' + data.response[key] + '</p>');
                }
                else if(key == 'current_city' ){
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
                    // $('#userlogin_response_message').after('<p class="hint">' + data.response_message + '</p>');
                }
            }
        });

    });
function open_dialog(text, title){
    $('#block_question').text(text);
    $('.ui-dialog-titlebar-close').empty()
    $('#block_question').dialog({
        modal: true,
        dialogClass: "no-close",
        draggable: false,
        title: title,
        buttons: [
            {
                text: "OK",
                click: function () {
                    $(this).dialog("close");
                    window.scrollTo(0, 0);
                }
            }
        ]
    });
    $('.ui-dialog-titlebar-close').html('<span>X</span>')
  }
  function open_dialog_with_url(text, title, url){
    $('#block_question').text(text);
    $('.ui-dialog-titlebar-close').empty()
    $('#block_question').dialog({
        modal: true,
        dialogClass: "no-close",
        draggable: false,
        title: title,
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
   $('#upload_resume_id').click(function (e) {
          e.preventDefault()
            $('#user_register_resume').click();
        });
      $('#user_register_resume').change(function(){
          $('#upload_resume_id').hide()
          $('#user_register_resume').show()
        });

$('.add_another').click(function(e){
    $(this).closest('form').submit();
    $(this).addClass('save_other')
})