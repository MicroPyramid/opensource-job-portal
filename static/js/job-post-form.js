/**
 * Job Post Form JavaScript
 * Handles all the functionality for the job posting form
 */

// Global variables
var jobFormHandler = {
    init: function() {
        this.initializePlugins();
        this.bindEvents();
        this.initializeDatePickers();
        this.initializeEditors();
    },

    initializePlugins: function() {
        // Initialize Select2
        $(".select2").select2({ 
            placeholder: 'Select or Start typing'
        });

        // Initialize DateTime Picker
        var date = new Date();
        $("#published_date").datetimepicker({
            collapse: false,
            sideBySide: true,
            useCurrent: false,
            showClose: true,
            format: "m/d/Y H:i:s",
            defaultTime: date.setMinutes(date.getMinutes() + 10)
        });

        // Initialize time picker
        $('#walkin_time').timepicker({
            showMeridian: true,
            defaultTime: false
        });

        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    },

    initializeDatePickers: function() {
        // Last date picker
        $("#last_date").datepicker({
            changeMonth: true,
            changeYear: true,
            yearRange: "2015:2050",
            dateFormat: "mm/dd/yy"
        });
        
        // Walk-in date pickers
        $("#walkin_from_date").datepicker({
            changeMonth: true,
            changeYear: true,
            yearRange: "2015:2050",
            dateFormat: "mm/dd/yy"
        });
        
        $("#walkin_to_date").datepicker({
            changeMonth: true,
            changeYear: true,
            yearRange: "2015:2050",
            dateFormat: "mm/dd/yy"
        });
    },

    initializeEditors: function() {
        // Check if TinyMCE is loaded
        if (typeof tinymce === 'undefined') {
            console.error('TinyMCE is not loaded. Please check the CDN link.');
            // Fallback to basic textarea functionality
            this.setupTextareaFallback();
            return;
        }

        console.log('TinyMCE version:', tinymce.majorVersion);

        // Initialize TinyMCE for Job Description
        tinymce.init({
            selector: '#textareacontents',
            height: 300,
            menubar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic forecolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
            content_style: 'body { font-family: Inter, sans-serif; font-size: 14px; margin: 10px; }',
            branding: false,
            promotion: false,
            paste_as_text: true,
            paste_auto_cleanup_on_paste: true,
            paste_remove_styles: true,
            paste_remove_styles_if_webkit: true,
            paste_strip_class_attributes: 'all',
            init_instance_callback: function (editor) {
                console.log('Job Description TinyMCE editor initialized:', editor.id);
            },
            setup: function (editor) {
                editor.on('change', function () {
                    editor.save(); // Save content to textarea
                });
            }
        });

        // Initialize TinyMCE for Company Description
        tinymce.init({
            selector: '#contents',
            height: 300,
            menubar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic forecolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
            content_style: 'body { font-family: Inter, sans-serif; font-size: 14px; margin: 10px; }',
            branding: false,
            promotion: false,
            paste_as_text: true,
            paste_auto_cleanup_on_paste: true,
            paste_remove_styles: true,
            paste_remove_styles_if_webkit: true,
            paste_strip_class_attributes: 'all',
            init_instance_callback: function (editor) {
                console.log('Company Description TinyMCE editor initialized:', editor.id);
            },
            setup: function (editor) {
                editor.on('change', function () {
                    editor.save(); // Save content to textarea
                });
            }
        });
    },

    setupTextareaFallback: function() {
        // If TinyMCE fails to load, provide basic functionality
        console.log('Setting up textarea fallback for rich text editors');
        
        $('#textareacontents, #contents').on('focus', function() {
            $(this).removeClass('border-red-500');
        });
    },

    bindEvents: function() {
        var self = this;
        
        // Job post selection events
        this.bindJobPostEvents();
        
        // Form submission events
        this.bindFormSubmissionEvents();
        
        // Modal events
        this.bindModalEvents();
        
        // Location management events
        this.bindLocationEvents();
        
        // Experience dropdown events
        this.bindExperienceEvents();
    },

    bindJobPostEvents: function() {
        // Handle job post empty option click
        $("#jobpost option[id='#empty']").click(function(){
            window.location = "/recruiter/job/"+$('#job_type').val()+"/new/";
        });
        
        // Handle job post type buttons
        $('.jobpost').click(function(e){
            var id = $(this).attr('id');
            if(id == "active"){
                $(this).addClass("active_class");
                $("#inactive").removeClass("active_class");
                $(this).removeClass("bg-gray-200 text-gray-700").addClass("bg-blue-500 text-white");
                $("#inactive").removeClass("bg-blue-500 text-white").addClass("bg-gray-200 text-gray-700");
            } else {
                $(this).addClass("active_class");
                $("#active").removeClass("active_class");
                $(this).removeClass("bg-gray-200 text-gray-700").addClass("bg-blue-500 text-white");
                $("#active").removeClass("bg-blue-500 text-white").addClass("bg-gray-200 text-gray-700");
            }
            
            var count = $('select#jobpost option[id='+ id +']').length;
            if (count == 0){
                $('select#jobpost option[id=empty]').text('There are no jobs');
            } else {
                var text = (id == 'active') ? 'Select From Active Jobs To Autofill' : 'Select From Inactive Jobs To Autofill';
                $('select#jobpost option[id=empty]').text(text);
            }
            
            $("select#jobpost").val('');
            $('.jobpost').removeClass('active');
            $(this).addClass('active');
            $('select#jobpost option').addClass('hidden');
            $('select#jobpost option[id='+ id +']').removeClass('hidden');
        });
        
        // Handle job post selection from dropdown
        $("select#jobpost").on('change', function(e) {
            var jobpost_id = $(this).val();
            var option_id = $('select#jobpost option:selected').attr('id');
            $('.jobpost').removeClass('active');
            $('#'+option_id).addClass('active');
            
            if (jobpost_id == ''){
                // Handle based on user type - this will be set by the template
                window.location = window.jobFormConfig.newJobUrl;
            } else {
                var job_type = $('#job_type').val();
                window.location = window.jobFormConfig.copyJobBaseUrl + job_type + '/copy/?jobpost_id=' + jobpost_id;
            }
        });
    },

    bindFormSubmissionEvents: function() {
        var self = this;
        
        // Handle form submission - Preview button
        $("#preview").click(function(e) {
            e.preventDefault();
            $('#status').val('Pending');
            
            var form_data = $('#jobform').serializeArray();
            self.processOtherFields(form_data);
            
            // Get content from TinyMCE editors if available
            if (typeof tinymce !== 'undefined' && tinymce.get('textareacontents') && tinymce.get('contents')) {
                $("input[name='description']").val(tinymce.get('textareacontents').getContent());
                $("input[name='company_description']").val(tinymce.get('contents').getContent());
            } else {
                // Fallback to textarea values if TinyMCE is not available
                $("input[name='description']").val($('#textareacontents').val());
                $("input[name='company_description']").val($('#contents').val());
            }
            
            var form = $('#jobform');
            var job_form_data = new FormData(form[0]);
            
            $.ajax({
                type: 'POST',
                dataType: 'json',
                data: job_form_data,
                enctype: 'multipart/form-data',
                processData: false,
                contentType: false,
                url: '.',
                success: function (data) {
                    // Show loading indicator - use BlockUI if available, otherwise show Tailwind loading
                    if (typeof $.blockUI === 'function') {
                        $.blockUI({ 
                            message: '<div class="bg-white rounded-lg p-6 shadow-lg"><div class="flex items-center"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div><span class="text-lg font-medium">Please Wait...</span></div></div>',
                            css: {
                                border: 'none',
                                padding: '15px',
                                backgroundColor: 'transparent',
                                '-webkit-border-radius': '10px',
                                '-moz-border-radius': '10px',
                                opacity: 0.9,
                                color: '#fff'
                            }
                        });
                    } else {
                        // Fallback loading indicator using Tailwind
                        self.showLoadingIndicator();
                    }
                    
                    if (data.error) {
                        self.handleFormErrors(data);
                    } else {
                        // Hide loading indicator
                        if (typeof $.unblockUI === 'function') {
                            $.unblockUI();
                        } else {
                            self.hideLoadingIndicator();
                        }
                        window.location = window.jobFormConfig.previewUrl + data.post + '/';
                    }
                },
                error: function(xhr, status, error) {
                    // Hide loading indicator on error
                    if (typeof $.unblockUI === 'function') {
                        $.unblockUI();
                    } else {
                        self.hideLoadingIndicator();
                    }
                    console.error('Form submission error:', error);
                    alert('An error occurred while submitting the form. Please try again.');
                }
            });
        });
    },

    bindModalEvents: function() {
        // Handle modal dismiss
        $('[data-dismiss="modal"]').click(function() {
            $('#myModal').addClass('hidden');
        });
        
        $('[data-dismiss="alert"]').click(function() {
            $(this).closest('#errors_display').addClass('hidden').removeClass('block');
        });
    },

    bindLocationEvents: function() {
        // Add location functionality
        $("body").on("click", "#another_location", function(e){
            var last_interview_location = $('div.interview_location').length;
            var location_count = last_interview_location + 1;
            var location_name = 'location_' + location_count;
            var searchbox_name = 'search_' + location_count;
            
            $('#location_name').val(location_name);
            $('#searchbox_name').val(searchbox_name);
            
            // Add new interview location div
            var newLocationHtml = `
                <div class="interview_location border border-gray-200 rounded-md p-4 relative mt-4" id="interview_location_${location_count}">
                    <button type="button" class="absolute top-2 right-2 text-red-500 hover:text-red-700 delete-interview">
                        <i data-lucide="trash-2" class="w-4 h-4 delete_location"></i>
                    </button>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Venue Details</label>
                        <textarea class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" name="venue_details_${location_count}" id="venue_details_${location_count}" rows="4" placeholder="Enter interview venue details, address, and directions..."></textarea>
                    </div>
                </div>`;
            
            $("#another_location").before(newLocationHtml);
            
            // Reinitialize icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        });
        
        // Delete location functionality
        $("body").on("click", "i.delete_location", function(e){
            if ($('.interview_location').length > 1){
                $(this).closest('.interview_location').remove();
            } else {
                alert('Job Post Should Contain At least One Interview Location');
            }
        });
    },

    bindExperienceEvents: function() {
        // Handle experience dropdowns
        $("select#min_year").on('change', function(e) {
            $('select#max_year').val('');
            $('select#max_year option').addClass('hidden');
            for(var i = $('select#min_year option:selected').attr('id'); i < $('select#min_year option').length; i++) {
                $('select#max_year option[id='+ i +']').removeClass('hidden');
            }
        });

        $("select#min_month").on('change', function(e) {
            $('select#max_month').val('');
            if($('select#max_year').val() == $('select#min_year').val()) {
                $('select#max_month option').addClass('hidden');
                for(var i = $('select#min_month option:selected').attr('id'); i < $('select#min_month option').length; i++) {
                    $('select#max_month option[id='+ i +']').removeClass('hidden');
                }
            } else {
                $('select#max_month option').removeClass('hidden');
            }
        });

        $("select#max_year").on('change', function(e) {
            $('select#max_month').val('');
            if($('select#max_year').val() == $('select#min_year').val()) {
                $('select#max_month option').addClass('hidden');
                for(var i = $('select#min_month option:selected').attr('id'); i < $('select#min_month option').length; i++) {
                    $('select#max_month option[id='+ i +']').removeClass('hidden');
                }
            } else {
                $('select#max_month option').removeClass('hidden');
            }
        });
    },

    processOtherFields: function(form_data) {
        console.log("other fields");
        var industry = [];
        var functional_area = [];
        var edu_qualification = [];
        var skills = [];
        var interview_location = [];
        var venue_details = [];
        var interview_location_count = $('div.interview_location').length;
        
        jQuery.each(form_data, function(i, field) {
            if (field['name'].indexOf('other_industry_name') >= 0){
                var industry_temp = {};
                industry_temp[field['name']] = field['value'];
                industry.push(industry_temp);
            }
            if (field['name'].indexOf('interview_city') >= 0){
                var interview_temp = {};
                interview_temp[field['name']] = field['value'];
                interview_location.push(interview_temp);
            }
            if (field['name'].indexOf('venue_details') >= 0){
                var interview_temp = {};
                interview_temp[field['name']] = field['value'];
                venue_details.push(interview_temp);
            }
            if (field['name'].indexOf('other_functional_area') >= 0){
                var functional_area_temp = {};
                functional_area_temp[field['name']] = field['value'];
                functional_area.push(functional_area_temp);
            }
            if (field['name'].indexOf('other_edu_qualification') >= 0){
                var edu_qualification_temp = {};
                edu_qualification_temp[field['name']] = field['value'];
                edu_qualification.push(edu_qualification_temp);
            }
            if (field['name'].indexOf('other_skill_name') >= 0){
                var skills_temp = {};
                skills_temp[field['name']] = field['value'];
                skills.push(skills_temp);
            }
        });
        
        console.log(JSON.stringify(interview_location));
        console.log(JSON.stringify(venue_details));
        
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_functional_area" id="final_functional_area" style="display:none;">'+ JSON.stringify(functional_area) +'</textarea>');
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_skills" id="final_skills" style="display:none;">'+ JSON.stringify(skills) +'</textarea>');
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_edu_qualification" id="final_edu_qualification" style="display:none;">'+ JSON.stringify(edu_qualification) +'</textarea>');
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_industry" id="final_industry" style="display:none;">'+ JSON.stringify(industry) +'</textarea>');
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_interview_location" id="final_interview_location" style="display:none;">'+ JSON.stringify(interview_location) +'</textarea>');
        $("#jobform").append('<textarea class="form-control other_functional_area" name="final_venue_details" id="final_venue_details" style="display:none;">'+ JSON.stringify(venue_details) +'</textarea>');
        
        $('#no_of_interview_location').val(interview_location_count);
    },

    handleFormErrors: function(data) {
        // Hide loading indicator
        if (typeof $.unblockUI === 'function') {
            $.unblockUI();
        } else {
            this.hideLoadingIndicator();
        }
        
        $("#errors_display").removeClass('hidden').addClass('block');
        var err_len = Object.keys(data.response).length;
        $("#error_count").html("<strong>There are "+err_len+" error(s) in the Form</strong>");
        $('div.error').remove();
        $('.border-red-500').removeClass('border-red-500');
        
        for (var key in data.response) {
            if(key == 'description'){
                // Add error styling to TinyMCE container if available
                if (typeof tinymce !== 'undefined' && tinymce.get('textareacontents')) {
                    var editorContainer = tinymce.get('textareacontents').getContainer();
                    $(editorContainer).addClass('border-red-500');
                }
            }
            if(key == 'company_description'){
                // Add error styling to TinyMCE container if available
                if (typeof tinymce !== 'undefined' && tinymce.get('contents')) {
                    var editorContainer = tinymce.get('contents').getContainer();
                    $(editorContainer).addClass('border-red-500');
                }
            }
            $('#' + key).removeClass('border-gray-300').addClass('border-red-500');
            if (data.response[key][0] != 'This field is required.' && data.response[key] != 'This field is required.'){
                $('#' + key).after('<div class="error text-red-500 text-sm mt-1">' + data.response[key] + '</div>');
            }
        }
        $(window).scrollTop(0);
    },

    // Fallback loading indicator methods when BlockUI is not available
    showLoadingIndicator: function() {
        // Create loading overlay using Tailwind classes
        var loadingHtml = `
            <div id="custom-loading-overlay" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 shadow-lg">
                    <div class="flex items-center">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div>
                        <span class="text-lg font-medium text-gray-900">Please Wait...</span>
                    </div>
                </div>
            </div>
        `;
        $('body').append(loadingHtml);
    },

    hideLoadingIndicator: function() {
        $('#custom-loading-overlay').remove();
    }
};

// Note: Initialization is handled in the template
