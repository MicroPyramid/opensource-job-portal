$(".month").click(function(e){
  e.preventDefault();
  $("#month").val($(this).attr("data"));
  $("#calander_form").attr("action", $(this).attr("href"));
  $("#calander_form").submit();
})

$(".week").click(function(e){
  e.preventDefault();
  $("#week").val($(this).attr("data"));
  $("#month").val($(this).attr("data_month"));
  $("#calander_form").attr("action", $(this).attr("href"));
  $("#calander_form").submit();
})

$(".full_year_view").click(function(e){
  e.preventDefault();
  $("#year").val($(this).attr("data"));
  $("#calander_form").attr("action", $(this).attr("href"));
  $("#calander_form").submit();
})

$(".full_month_view").click(function(e){
  e.preventDefault();
  $("#month").val($(this).attr("data"));
  $("#calander_form").attr("action", $(this).attr("href"));
  $("#calander_form").submit();
})

$(".prev_next").click(function(e){
  e.preventDefault();
  $("#year").val($(this).attr("data"));
  $("#calander_form").attr("action", window.location.pathname);
  $("#calander_form").submit();
})

$(".prev_next_month").click(function(e){
  e.preventDefault();
  if ($(this).attr("data") == 1){
    if ($(this).attr("data_event") == "prev"){
      if ($($(".prev_next_month")[1]).attr("data") == 11){
        $("#year").val(parseInt($("#year").val())-1);
      }
    }else{
      $("#year").val(parseInt($("#year").val())+1);
    }
  }
  if ($(this).attr("data") == 12){
    if ($(this).attr("data_event") == "prev"){
      $("#year").val(parseInt($("#year").val())-1);
    }
  }
  $("#month").val($(this).attr("data"));
  $("#calander_form").attr("action", window.location.pathname);
  $("#calander_form").submit();
})

$("#week_calendar").change(function(e){
  e.preventDefault();
  $("#week").val($(this).val());
  $("#month").val($('#month_calendar').val());
  path = '/calendar/' + $('#year').val() + '/month/' + $('#month_calendar').val() + '/week/' + $('#week_calendar').val() + '/'
  $("#calander_form").attr("action", path);
  $("#calander_form").submit();
})

$("#month_calendar").change(function(e){
  e.preventDefault();
  $("#month").val($(this).val());
  $("#week").val($('#week_calendar').val());
  path = '/calendar/' + $('#year').val() + '/month/' + $('#month_calendar').val() + '/'
  $("#calander_form").attr("action", path);
  $("#calander_form").submit();
})

// $(".project_overview").click(function(e){
//   e.preventDefault();
//   var date = $(this).attr("data") + "-" + $(this).attr("data_month") + "-" + $(this).attr("data_date")
//   $("#deadline").val(date);
//   $("#calander_form").attr("action", $(this).attr("href"));
//   $("#calander_form").submit();
// })
