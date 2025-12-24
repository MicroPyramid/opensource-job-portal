$(document).ready(function($) {
  // browser window scroll (in pixels) after which the "back to top" link is shown
  var offset = 300,
    //browser window scroll (in pixels) after which the "back to top" link opacity is reduced
    offset_opacity = 1200,
    //duration of the top scrolling animation (in ms)
    scroll_top_duration = 700,
    //grab the "back to top" link
    $back_to_top = $('.cd-top');

  //hide or show the "back to top" link
  $(window).scroll(function() {
    ($(this).scrollTop() > offset) ? $back_to_top.addClass(
      'cd-is-visible'): $back_to_top.removeClass(
      'cd-is-visible cd-fade-out');
    if ($(this).scrollTop() > offset_opacity) {
      $back_to_top.addClass('cd-fade-out');
    }
  });

  //smooth scroll to top
  $back_to_top.on('click', function(event) {
    event.preventDefault();
    $('body,html').animate({
      scrollTop: 0,
    }, scroll_top_duration);
  });
});
skills = $('#filter_skill').val()
locations = $('#filter_location').val()
if(skills){skills = skills.trim().split(',')}
if(locations){locations = locations.trim().split(',')}
for (each in skills) {
  if (skills[each] != '') {
    $('.jobs_list').highlight(skills[each].trim())
    $('.right_container').highlight(skills[each].trim())
  }
}
for (each in locations) {
  if (locations[each] != '') {
    if (locations[each] != '') {

      $('.jobs_list, .right_container').highlight(locations[each].trim())
      $('.right_container').highlight(locations[each].trim())
    }
  }
}
$(".send_mail").click(function(e){
  e.preventDefault()
  verified = $(this).hasClass('active')
  completed = $(this).hasClass('completed')
  logged = $(this).hasClass('logged')
  if(verified && completed && logged){
    window.location = $(this).attr('href')
  }
  else{
    if(!logged){
      $('.job_seeker').click();
    }
    else if(!verified){
      open_dialog('You need to verify your Email to apply For this Job', 'Info!')
    }
    else if(!completed){
      open_dialog_with_url('Please complete your profile to apply for this job', 'Info!', '/profile/')
    }
  }
})

function validateForm() {
  var qs = document.forms["search-form"]["q"].value;
  var ql = document.forms["search-form"]["location"].value;
  var job_type = $("#job_type").val()
  if(!job_type){
    var job_type = $("input[name=job_type]:checked").val()
  }
  if (qs == null || qs == "" && ql == '') {
    open_dialog('Please select atleast one Skill or Location',
      'info!')
    return false;
  } else {
      $.ajax({
        url: '/get/search-slugs/',
        async: false,
        data: {
          'q_slug': qs,
          'location': ql
        },
        success: function(data) {
          slug = data.skill_slug
          location_slug = data.location_slug
        }
      })
    if (qs.length > 0 && ql.length > 0) {
      if (job_type == 'Fresher') {
        url = '/' + slug + '-fresher-jobs-in-' + location_slug + '/'
      } else if (job_type == 'walk-in') {
        url = '/' + slug + '-walkins-in-' + location_slug + '/'
      } else {
        url = '/' + slug + '-jobs-in-' + location_slug + '/'
      }
    }
    if (qs.length > 0 && ql.length == 0) {
      if (job_type == 'Fresher') {
        url = '/' + slug + '-fresher-jobs/'
      } else if (job_type == 'walk-in') {
        url = '/' + slug + '-walkins/'
      } else {
        url = '/' + slug + '-jobs/'
      }
    }
    if (ql.length > 0 && qs.length == 0) {
      if (job_type == 'Fresher') {
        url = '/fresher-jobs-in-' + location_slug + '/'
      } else if (job_type == 'walk-in') {
        url = '/walkins-in-' + location_slug + '/'
      } else {
        url = '/jobs-in-' + location_slug + '/'
      }
    }
    if (job_type && job_type != 'Fresher' && job_type != 'walk-in') {
      url += '?job_type=' + job_type
    }
    document.forms["search-form"].action = url;
    return true;
  }
}

$("#other_loc").click(function(e){
    $(this).parent().find('.hint').remove()
    if($(this).is(":checked")){
    $('.current').hide()
    $("#user_register_other_location").show()
    }
  else{
    $('.current').show()
    $("#user_register_other_location").hide()
  }
})

$('.job_apply_login').click(function(e) {
  e.preventDefault();
  // $('#demo').plainModal('open');
  $('p.hint').remove();
  $('.job_seeker').click();
  $.post('/jobs/applied_for/', {
    'job_id': $(this).attr('id')
  }, function(data) {}, 'json')
})
$("a.applicant_apply").click(function(e) {
  e.preventDefault();
  href = $(this).attr('data-href')
  $.post('/jobs/apply/' + $(this).attr('id') + '/', {}, function(
    data) {
    if (data.error) {
      if(data.url){
        open_dialog_with_url(data.response, 'Error!', data.url)
      }
      else{
        open_dialog(data.response, 'Error!')
      }
    } else {
      open_dialog_with_url(data.response, 'Info!', data.url)
    }
  }, 'json');
});


var Autocomplete = function(options) {
    this.form_selector = options.form_selector
    this.url = '/search/skill-auto/' || options.url
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length ||
        1)
    this.form_elem = null
    this.query_box = null
}
Autocomplete.prototype.setup = function() {
    var self = this

    this.form_elem = $(this.form_selector)
    this.query_box = this.form_elem.find('input[name=q]')

    this.query_box.on('keyup', function() {
        var query = self.query_box.val().split(
            ', ').slice(-
            1)[0]
        if (self.query_box && query.trim().length <
            self.minimum_length) {
            $('.ac-skillresults').remove()
            return false
        }

        self.fetch(query)
    })

    this.form_elem.on('click', '.ac-result', function(ev) {
        old_str = document.getElementsByName("q")[
            0].value;
        if (old_str.lastIndexOf(', ') > 0) {
            document.getElementsByName("q")[0].value =
                old_str.substr(0, old_str.lastIndexOf(
                    ', ') + 2) +
                $(this).text() + ', ';
        } else {
            document.getElementsByName("q")[0].value =
                $(this)
                .text() + ', ';
        }
        $('.ac-skillresults').remove()
        return false
    })
}

Autocomplete.prototype.fetch = function(query) {
    var self = this

    $.ajax({
        url: this.url,
        data: {
            'q': query
        },
        success: function(data) {
            self.show_results(data)
        }
    })
}

Autocomplete.prototype.show_results = function(data) {
    $('.ac-skillresults').remove()
    var results = data.results || []
    var results_wrapper = $(
        '<div class="ac-skillresults"></div>')
    var base_elem = $(
        '<div class="result-wrapper"><a href="" class="ac-result"></a><br><p class="auther"></p></div>'
    )
    if (results.length > 0) {
        for (var res_offset in results) {
            elem = $(
                '<div class="result-wrapper"><a data-href="' +
                results[res_offset]['slug'] +
                '" class="ac-result"><span>' +
                results[res_offset]
                ['name'] + '</span></a></div>');
            results_wrapper.append(elem);
        }
    } else {
        return false
    }

    this.query_box.after(results_wrapper)
}

$(document).ready(function() {
    window.autocomplete = new Autocomplete({
        form_selector: '.autocomplete-me'
    })
    window.autocomplete.setup()
});
var AutocompleteCity = function(options) {
    this.form_selector = options.form_selector
    this.url = '/search/city-auto/' || options.url
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length ||
        1)
    this.form_elem = null
    this.query_box = null
}

AutocompleteCity.prototype.setup = function() {
    var self = this

    this.form_elem = $(this.form_selector)
    this.query_box = this.form_elem.find(
        'input[name=location]')
    this.query_box.on('keyup', function() {
        var query = self.query_box.val().split(
            ', ').slice(-
            1)[0]

        if (self.query_box && query.trim().length <
            self.minimum_length) {
            $('.ac-cityresults').remove()
            return false
        }

        self.fetch(query)
    })

    this.form_elem.on('click', '.ac-cityresult', function(
        ev) {
        // self.query_box.val($(this).text())
        old_str = document.getElementsByName(
                "location")[0]
            .value;
        if (old_str.lastIndexOf(', ') > 0) {
            document.getElementsByName("location")[
                    0].value =
                old_str.substr(0, old_str.lastIndexOf(
                    ', ') + 2) +
                $(this).text() + ', ';
        } else {
            document.getElementsByName("location")[
                    0].value =
                $(this).text() + ', ';
        }
        $('.ac-cityresults').remove()
        return false
    })
}

AutocompleteCity.prototype.fetch = function(query) {
    var self = this

    $.ajax({
        url: this.url,
        data: {
            'location': query
        },
        success: function(data) {
            self.show_results(data)
        }
    })
}

AutocompleteCity.prototype.show_results = function(data) {
    $('.ac-cityresults').remove()
    var results = data.results || []
    var results_wrapper = $(
        '<div class="ac-cityresults"></div>')
    var base_elem = $(
        '<div class="result-wrapper"><a href="" class="ac-result"></a><br><p class="auther"></p></div>'
    )
    if (results.length > 0) {
        for (var res_offset in results) {
            elem = $(
                '<div class="result-wrapper"><a href="" class="ac-cityresult"><span>' +
                results[res_offset]['name'] +
                '</span></a></div>'
            );
            results_wrapper.append(elem);
        }
    } else {
        $('.ac-cityresults').remove()
        return false
    }

    this.query_box.after(results_wrapper)
}

var AutocompleteIndustry = function(options) {
    this.form_selector = options.form_selector
    this.url = '/search/industry-auto/' || options.url
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length ||
        1)
    this.form_elem = null
    this.query_box = null
}

AutocompleteIndustry.prototype.setup = function() {
    var self = this

    this.form_elem = $(this.form_selector)
    this.query_box = this.form_elem.find(
        'input[name=industry]')
    this.query_box.on('keyup', function() {
        var query = self.query_box.val()
        if (query.length < self.minimum_length) {
            $('.ac-industryresults').remove()
            return false
        }

        self.fetch(query)
    })

    this.form_elem.on('click', '.ac-industryresult',
        function(
            ev) {
            // self.query_box.val($(this).text())

            old_str = document.getElementsByName(
                    "industry")[0]
                .value;
            if (old_str.lastIndexOf(', ') > 0) {
                document.getElementsByName("industry")[
                        0].value =
                    old_str.substr(0, old_str.lastIndexOf(
                        ', ') + 2) +
                    $(this).text() + ', ';
            } else {
                document.getElementsByName("industry")[
                        0].value =
                    $(this).text() + ', ';
            }

            $('.ac-industryresults').remove()
            return false
        })
}

AutocompleteIndustry.prototype.fetch = function(query) {
    var self = this

    $.ajax({
        url: this.url,
        data: {
            'industry': query
        },
        success: function(data) {
            self.show_results(data)
        }
    })
}

AutocompleteIndustry.prototype.show_results = function(data) {
    $('.ac-industryresults').remove()
    var results = data.results || []
    var results_wrapper = $(
        '<div class="ac-industryresults"></div>')
    var base_elem = $(
        '<div class="result-wrapper"><a href="" class="ac-result"></a><br><p class="auther"></p></div>'
    )
    if (results.length > 0) {
        for (var res_offset in results) {
            elem = $(
                '<div class="result-wrapper"><a href="" class="ac-industryresult"><span>' +
                results[res_offset]['name'] +
                '</span></a></div>'
            );
            results_wrapper.append(elem);
        }
    } else {
        return false
    }

    this.query_box.after(results_wrapper)
}

var AutocompleteFunctionalArea = function(options) {
    this.form_selector = options.form_selector
    this.url = '/search/functional-area-auto/' || options
        .url
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length ||
        3)
    this.form_elem = null
    this.query_box = null
}

AutocompleteFunctionalArea.prototype.setup = function() {
    var self = this

    this.form_elem = $(this.form_selector)
    this.query_box = this.form_elem.find(
        'input[name=functional_area]')
    this.query_box.on('keyup', function() {
        var query = self.query_box.val()

        if (query.length < self.minimum_length) {
            $('.ac-functionalarearesults').remove()
            return false
        }

        self.fetch(query)
    })

    this.form_elem.on('click', '.ac-functionalarearesult',
        function(ev) {
            // self.query_box.val($(this).text())

            old_str = document.getElementsByName(
                "functional_area")[0].value;
            if (old_str.lastIndexOf(', ') > 0) {
                document.getElementsByName(
                        "functional_area")[0].value =
                    old_str.substr(0, old_str.lastIndexOf(
                        ', ') + 2) +
                    $(this).text() + ', ';
            } else {
                document.getElementsByName(
                        "functional_area")[0].value =
                    $(this).text() + ', ';
            }

            $('.ac-functionalarearesults').remove()
            return false
        })
}

AutocompleteFunctionalArea.prototype.fetch = function(query) {
    var self = this

    $.ajax({
        url: this.url,
        data: {
            'functional_area': query
        },
        success: function(data) {
            self.show_results(data)
        }
    })
}

AutocompleteFunctionalArea.prototype.show_results = function(
    data) {
    $('.ac-functionalarearesults').remove()
    var results = data.results || []
    var results_wrapper = $(
        '<div class="ac-functionalarearesults"></div>'
    )
    var base_elem = $(
        '<div class="result-wrapper"><a href="" class="ac-result"></a><br><p class="auther"></p></div>'
    )
    if (results.length > 0) {
        for (var res_offset in results) {
            elem = $(
                '<div class="result-wrapper"><a href="" class="ac-functionalarearesult"><span>' +
                results[res_offset]['name'] +
                '</span></a></div>'
            );
            results_wrapper.append(elem);
        }
    } else {
        return false
    }

    this.query_box.after(results_wrapper)
}

$(document).ready(function() {
    window.autocompleteCity = new AutocompleteCity({
        form_selector: '.autocomplete-me'
    })
    window.autocompleteCity.setup()

    window.AutocompleteIndustry = new AutocompleteIndustry({
        form_selector: '.autocomplete-me'
    })
    window.AutocompleteIndustry.setup()

    window.AutocompleteFunctionalArea = new AutocompleteFunctionalArea({
        form_selector: '.autocomplete-me'
    })
    window.AutocompleteFunctionalArea.setup()
});


$('#similar_job_alert').click(function () {
  reset_menu();
  $('p.hint').remove();
  $('.overlay_div').show();
  $('#CreateSimilarAlert')[0].reset()
  $("#create_similarjob_alert").show()
})
  $('form#CreateSimilarAlert').ajaxForm({
      type: 'POST',
      dataType: 'json',
      data: $('#CreateSimilarAlert').serialize(),
      url: '/alert/create/',
      success: function (data) {
          if (data.error == false) {
              $('p.hint').remove();
              reset_menu();
              $("#create_similarjob_alert").hide()
              open_dialog('Success, We will reach you with Jobs of this type', 'Success!')
          }
          else {
              $('p.hint').remove();
              for (var key in data.message) {
                  $('#alert_' + key).after('<p class="hint">' + data.message[key] + '</p>');
              }
          }
      }
  })