  $('.file_upload').click(function (e) {
          e.preventDefault()
            $('#file_input').click();
        });
        $('#file_input').change(function(){
          $("form#profilepicform").submit()
        });

        $('form#profilepicform').ajaxForm({
            type: 'POST',
            dataType: 'json',
            url: "/my/upload_profilepic/",
            data: $('#profilepicform').serialize(),
            success: function (data) {
                if (data.error == false) {
                  open_dialog_with_url(data.data, 'Info!', '.')
                } else {
                  open_dialog(data.data, 'Info!')
                }
            }
        });
 $ = jQuery;
        $(document).ready(function () {

            current_block = $('.skip_block.show');
            if($(current_block).next('.skip_block').length>0){
              $('.skip_block.show').find('.skip_previous').remove()
            }
            else{
              skip_block = $('.skip_block.hide')[0];
              $(skip_block).removeClass('hide').addClass('show');
              $(skip_block).find('.skip_previous').remove()
            }

            // Setup the ajax indicator
            // $('body').append('<div id="ajaxBusy"><p><img src="http://peeljobs.s3.amazonaws.com/static/img/loader-gif.gif" height="60px" width="60px"></p></div>');
            // $('#ajaxBusy').css({
            //     display: "block",
            //     margin: "0px",
            //     paddingLeft: "0px",
            //     paddingRight: "0px",
            //     paddingTop: "0px",
            //     paddingBottom: "0px",
            //     position: "absolute",
            //     left: "55%",
            //     top: "55%",
            //     width: "auto",
            // });

            $(".download").click(function (e) {
                e.preventDefault();
                window.location = $(this).attr('id');
            });
        });

        function submitform() {
            $('form#resumeupload').submit();
        }

        $('form#resumeupload').ajaxForm({
            url: '/upload_resume/',
            type: 'POST',
            dataType: 'json',
            data: $('#resumeupload').serialize(),
            success: function (data) {
                if (data.error == false) {
                    window.location = ".";
                } else {
                  open_dialog(data.data, 'Info!')
                }
            }
        });

        $('.delete-resume').click(function (e) {
            var myPos = [ $(window).width() / 2, 50 ];
            e.preventDefault();
            e.stopPropagation();
            $('#block_question').text('Do you want to delete Resume?')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                title: "Info!!",
                position: myPos,
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post("/my/delete-resume/", {}, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                                open_dialog_with_url('Your resume has been deleted successfully', 'Success!',".")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                            return;
                        }
                    }
                ]
            });
          $('.ui-dialog-titlebar-close').html('<span>X</span>')
        });
        $("a.language-delete").click(function (e) {
            e.preventDefault();
            e.stopPropagation();
            url = $(this).attr('href')
            data = $(this).attr('id')
            var myPos = [ $(window).width() / 2, 50 ];
            $('#block_question').text('Do you want to delete language?')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                position: myPos,
                title: "Info!!",
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post(url, data, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                              open_dialog_with_url('Language deleted successfully', 'Succes!', 
                                "/profile/")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                        }
                    }
                ]
            });
  $('.ui-dialog-titlebar-close').html('<span>X</span>')
        });

  $("a.employment-delete").click(function (e) {
            var myPos = [ $(window).width() / 2, 50 ];
            e.preventDefault();
            e.stopPropagation();
            data = $(this).attr('id')
            url = $(this).attr('href')
            $('#block_question').text('Do you want to delete Experience Details?')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                title: "Info!!",
                position: myPos,
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post(url, data, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                            open_dialog_with_url('Your profile has been updated successfully', 'Succes!',
                              "/profile/")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                        }
                    }
                ]
            });
          $('.ui-dialog-titlebar-close').html('<span>X</span>')
        });

        $("a.education-delete").click(function (e) {
            var myPos = [ $(window).width() / 2, 50 ];
            e.preventDefault();
            e.stopPropagation();
            url = $(this).attr('href')
            data = $(this).attr('id')
            $('#block_question').text('Do you want to delete Education Details?')
             $('.ui-dialog-titlebar-close').empty()
          $('.ui-dialog-titlebar-close').html('<span>X</span>')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                title: "Info!!",
                position: myPos,
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post(url, data, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                                  open_dialog_with_url('Education Details are Deleted Sucessfully', 'Success!',
                                    ".")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                        }
                    }
                ]
            });
            $('.ui-dialog-titlebar-close').html('<span>X</span>')
        });
        $("a.technicalskill-delete").click(function (e) {
            e.preventDefault();
            e.stopPropagation();
            href = $(this).attr('href')
            data = $(this).attr('id')
            $('#block_question').text('Do you want to delete Skill?')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                title: "Info!!",
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post(href, data, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                                  open_dialog_with_url('Technical Skill is Deleted Sucessfully', 'Success!',
                                    ".")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                        }
                    }
                ]
            });
                      $('.ui-dialog-titlebar-close').html('<span>X</span>')

        });
        $("a.project-delete").click(function (e) {
            var myPos = [ $(window).width() / 2, 50 ];
            e.preventDefault();
            e.stopPropagation();
            url = $(this).attr('href')
            data = $(this).attr('id')
            $('#block_question').text('Do you want to delete Project?')
            $('#block_question').dialog({
                modal: true,
                draggable: false,
                title: "Info!!",
                position: myPos,
                buttons: [
                    {
                        text: "Yes",
                        click: function () {
                            $(this).dialog("close");
                            $.post(url, data, function (data) {
                                if (data.error) {
                                  open_dialog(data.response, 'Error!')
                                } else {
                                  open_dialog_with_url('Project Deleted Sucessfully', 'Success!', "/profile/")
                                }
                            }, 'json');
                        }
                    },
                    {
                        text: "No",
                        click: function () {
                            $(this).dialog("close");
                        }
                    }
                ]
            });
                      $('.ui-dialog-titlebar-close').html('<span>X</span>')

        });

    $('form.profileform').submit(function(e){
        e.preventDefault();
        url = $(this).attr('data-href')
      var form = this;
      var formData = new FormData($(this)[0]);

        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: formData,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,

            url: url,
            success: function (data) {
                if (data.error == false) {
                    current_block = $('.skip_block.show');
                    console.log(current_block)
                    if($(current_block).next('.skip_block').length>0){
                      $('.applicant_profile_percantage').text(data.profile_percantage)
                      updating_profile_progress_percantage(data.profile_percantage)
                      if(data.upload_resume){
                        $('#resume_upload_icon').html("<i class='fa fa-check-circle'></i>")
                        $('.resume_block').show()
                        $('.resume_name').text(data.resume_name)
                        $('.download').attr('id', data.resume_path)
                        open_dialog(data.data, 'Success!');
                      }
                      if(data.personal_info){
                        $('#user_profile').html("<i class='fa fa-check-circle'></i>")
                        $('.first_name').text(data.first_name)
                        $('.resume_title').text(data.resume_title)
                        $('.mobile').text(data.mobile)
                        $('.dob').text(data.dob)
                        $('.current_city').text(data.current_city)
                        $('.nationality').text('India')
                        open_dialog('Personal Info Updated Sucessfully', 'Success!');
                      }
                      if(data.professional_info){
                        $('.year').text(data.year + ' Year(s) ' + data.month + ' Month(s)')
                        $('.job_role').text(data.job_role)
                        $('.prefered_industry').text(data.prefered_industry)
                        $('#professional_info_icon').html("<i class='fa fa-check-circle'></i>")
                        open_dialog('Professional Info Updated Sucessfully', 'Success!');
                      }
                      if(data.technical_skill){
                        $('#technical_skills_icon').html("<i class='fa fa-check-circle'></i>")
                        open_dialog('Technical Skills Updated Sucessfully', 'Success!');
                      }
                      $(current_block).next('.skip_block').removeClass('hide').addClass('show');
                      $(current_block).removeClass('show').addClass('hide');;
                }
                else{
                    open_dialog_with_url('Your Profile Updated successfully, Now you can apply for the jobs', "Success!!!", '.');
                }
                }
                else if (data.response) {
                    $('p.hint').remove();
                    for (var key in data.response) {
                      $('#profile_' + key).after('<p class="hint">' + data.response[key] + '</p>');
                    }
                }
                else {
                    $('p.hint').remove();
                    if (data.data){
                    open_dialog(data.data, 'Success!');
                  }
                  else{
                    open_dialog(data.response_message, 'Success!');
                    // $('#userlogin_response_message').after('<p class="hint">' + data.response_message + '</p>');
                  }
                }
            }
        });

    });
    $(function () {
        $(".datepicker").datepicker({
            changeMonth: true,
            changeYear: true,
            yearRange: "1950:2020"
        });
    });
            // Ajax activity indicator bound to ajax start/stop document events
        $(document).ajaxStart(function () {
            $('.modal_loading').show();
        }).ajaxStop(function () {
            $('.modal_loading').hide();
        });
        $(".skip_previous").click(function(){
          var current = $(this).parent().parent().attr('id')
          console.log(current)
          if(current== 'skip_resume'){
            var show = "skip_personal_info"
          }
          if(current== 'skip_skills'){
            if($("#skip_resume").attr('class')){
              var show = "skip_resume"
            }
            else{
            var show = "skip_personal_info"
            }
          }
          if(current== 'skip_professional'){
            if($("#skip_skills").attr('class')){
              var show = "skip_skills"
            }
             else if($("#skip_resume").attr('class')){
              var show = "skip_resume"
            }
            else{
            var show = "skip_personal_info"
            }
          }
          console.log(show)
            $(this).parent().parent().removeClass('show')
            $(this).parent().parent().addClass('hide')
            $('#'+show).removeClass('hide')
            $('#'+show).addClass('show')
        })

$("#email_notifications").click(function(e){
    e.preventDefault();
            $.post("/my/edit_emailnotifications/", {}, function (data) {
              if (data.error == true){
                    open_dialog('Something Went Wrong!', 'Alert!!!')
              }
              else{
                if (data.status == true) {
                  $("#on_note").removeClass()
                  $("#on_note").addClass('btn btn-xs btn-success')
                  $("#off_note").removeClass()
                  $("#off_note").addClass('btn btn-xs btn-default')
                    open_dialog_with_url('Email Notifications are Enabled', 'Success!!!', "/profile/")
                } else {
                 $("#on_note").removeClass()
                  $("#on_note").addClass('btn btn-xs btn-default')
                  $("#off_note").removeClass()
                  $("#off_note").addClass('btn btn-xs btn-danger')
                    open_dialog_with_url('Email Notifications are Disabled', 'Success!!!', "/profile/")
                }
              }
            }, 'json');
})
$("form#profiledescrptionform").submit(function (e) {
    e.preventDefault();
    $.post("/profile_description/edit/", $("form#profiledescrptionform").serialize(), function (data) {
        if (data.error) {
            $('p.hint').remove();
            for (var key in data.response) {
                $('#' + key).after('<p class="hint">' + data.response[key] + '</p>');
            }
        } else {
          open_dialog_with_url('Your profile has been updated successfully', 'Success!!!', ".")
        }
    }, 'json');
});
  $("form#professionalform").submit(function(e) {
      e.preventDefault();
      $.post("/professionalinfo/edit/", $("form#professionalform").serialize(), function(data) {
        if (data.error) {
          $('p.hint').remove();
          for (var key in data.response) {
            $('#' + key).after('<p class="hint">' + data.response[key] + '</p>');
          }
        } else {
          open_dialog_with_url('Your profile has been updated successfully', 'Success!!!', ".")
        }
      }, 'json');
    });
$("form#languageform").submit(function (e) {
              e.preventDefault();
              if ($('#edit_language').val() == 'True'){
                url = $('#lang_url').val()
              }
              else{
                url = '/language/add/'
              }
              $.post(url, $("form#languageform").serialize() , function (data) {
                  if (data.error) {
                      $('p.hint').remove();
                      if (data.response_message) {
                          open_dialog(data.response_message, 'Error!')
                      }
                      if (data.response) {
                          open_dialog(data.response, 'Info!')
                      }
                      if (data.language) {
                          open_dialog(data.language, 'Info!')
                      }
                  } else {
                    $('#edit_language').val('')
                    $('#edit_language').val('') 
                    $("#speak").prop('checked', false);
                    $("#write").prop('checked', false);
                    $("#read").prop('checked', false);
                    $('#lang_url').val('')
                        open_dialog_with_url('Your profile has been updated successfully', 'Success!!!', ".")
                  }
              }, 'json');
          });

// Profile Summery update
$(function () {
    $("#dob").datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: "1950:2020"
    });
});
$(document).ready(function () {
    $ = jQuery;
    $("select#preferred_city").select2({placeholder: "Select A City", maximumSelectionSize: 6});
    $("select#current_city").select2({placeholder: "Select A City", maximumSelectionSize: 6});
    $("select#industry").select2({placeholder: "Select A Industry", maximumSelectionSize: 6});
    $("select#functional_area").select2({placeholder: "Select A Functional Area", maximumSelectionSize: 6});

    $('#present_address').click(function () {
        if (document.getElementById('present_address').checked) {
            $("#permanent_address").val('');
            $("#permanent_address").val($("#address").val());
        }
        else {
            $("#permanent_address").val('');
        }
    });
});

$("form#personalform").submit(function (e) {
    e.preventDefault();
    $.post("/personalinfo/edit/", $("form#personalform").serialize(), function (data) {
        if (data.error) {
            $('p.hint').remove();
            for (var key in data.response) {
                $('#' + key).after('<p class="hint">' + data.response[key] + '</p>');
            }
        } else {
          open_dialog_with_url('Your profile has been updated successfully', 'Success!!!', ".")
        }
    }, 'json');
});
  $("#other_loc").change(function(e){
  $(this).parent().find('.hint').remove()
    if($(this).is(":checked")){
    $('#current_city').parent().find('.select2').hide()
    $("#another_location").show()
  }
  else{
    $('#current_city').parent().find('.select2').show()
    $("#another_location").hide()
  }
  })
$(".edit_this").click(function(e){
    e.preventDefault()
    $(this).hide()
    $(this).closest('.parent_block').find('.child1').hide()
    $(this).closest('.parent_block').find('.child2').show()
})
$(".cancelbutton").click(function(e){
  e.preventDefault()
  $(this).closest('.parent_block').find(".edit_this").show()
  $(this).closest('.parent_block').find('.child1').show()
  $(this).closest('.parent_block').find('.child2').hide()
})
$(".edit_language").click(function(e) {
  e.preventDefault()
  $(this).closest('.parent_block').find(".edit_this").hide()
  $('#lang_url').val($(this).attr('data-href'))
  $.post($(this).attr('data-href'), {'get_lang': true}, function (data) {
            if (data.error) {
                open_dialog('Something went wrong', 'Error!')
            } else {
              $("#language_id").val(data.id)
              $("#read").prop('checked', data.read == true)
              $("#write").prop('checked', data.write == true)
              $("#speak").prop('checked', data.speak == true)
              $('.show_lang').hide()
              $('.edit_lang').show()
              $('#edit_language').val('True')
            }
        }, 'json');
})
