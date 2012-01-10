$(function() {
   var requirements = {
      total: { regex: /.{8,}/, message: 'A minimum of 8 characters' },
      username: { regex: {
         test: function(password) {
            var username = $.trim($("#username").val());

            if (username != "") {
               return password.toLowerCase().indexOf(username.toLowerCase()) == -1;
            } else {
               return true;
            }
         }
      }, message: 'Must not contain your username' }
   }

   var requirement_classes = {
      numbers: { regex: /[0-9]+/, message: 'A number' },
      lower: { regex: /[a-z]+/, message: 'A lower case letter' },
      upper: { regex: /[A-Z]+/, message: 'An upper case letter' },
      special: { regex: /[^a-zA-Z0-9]+/, message: 'A special character' }
   }

   function test_requirement(requirement, password, class_name) {
      if (requirement.regex.test(password)) {
         $(class_name).append("<li class='passed'>" + requirement.message + "</li>");

         return true;
      } else {
         $(class_name).append("<li>" + requirement.message + "</li>");

         return false;
      }
   }

   function test_password() {
      $("#requirements").html('');
      $("#requirement-classes").html('');

      var passed = true;
      var general_passed = true;

      var classes = 0;

      var new_password = $("#new_password").val();
      var new_password_verify = $("#new_password_verify").val();

      for (var i in requirements) {
         if (!test_requirement(requirements[i], new_password, '#requirements')) {
            general_passed = false;
         }
      }

      if (general_passed) {
         $("#general-container").attr('class', 'passed');
      } else {
         $("#general-container").attr('class', '');
      }

      for (var i in requirement_classes) {
         if (test_requirement(requirement_classes[i], new_password, '#requirement-classes')) {
            classes++;
         }
      }

      if (classes < 3) {
         passed = false;

         $("#requirement-classes-container").attr('class', '');
      } else {
         $("#requirement-classes-container").attr('class', 'passed');
      }

      var matched = false;

      if (new_password != new_password_verify) {
         $("#match-requirement").show();
      } else {
         $("#match-requirement").hide();

         matched = true;
      }

      if (passed && general_passed) {
         $("#requirements-container").hide();
      } else {
         $("#requirements-container").show();
      }

      if (passed && general_passed && matched) {
         $('#validation').attr('class', 'passed');

         $('input[type=submit]').removeAttr('disabled');

         $('#pass-container').show();
      } else {
         $('#validation').attr('class', '');

         $('input[type=submit]').attr('disabled', 'disabled');

         $('#pass-container').hide();
      }
   }

   $("#new_password, #new_password_verify, #username").change(test_password);
   $("#new_password, #new_password_verify, #username").keyup(test_password);

   test_password();

   $('input[type=password], input[type=text]').hint({ method: 'valueSwap' });

   $('.rounded').corner('15px');
   $('#validation').corner('5px');

   var uri = parseUri(location.href);

   if (uri.queryKey.username) {
      $("#username").val(uri.queryKey.username);
      $("#username").removeClass('hint');
   }

   $('#password-entry-form').ajaxForm({
      'target': '#password-form-result',
      'success': function (responseText, statusText, xhr, $form) {
         if (responseText.indexOf('successfully') != -1) {
            $('#password-try-again-wrapper').hide();
         }

         $('#password-entry').slideUp();
         $('#password-form-result-wrapper').slideDown();
      }
   });

   $('#password-try-again').click(function () {
      $('#password-entry-form').resetForm();
      $('input[type=password], input[type=text]').hint({ method: 'valueSwap' });

      $('#password-form-result-wrapper').slideUp();
      $('#password-entry').slideDown();
   });
});
