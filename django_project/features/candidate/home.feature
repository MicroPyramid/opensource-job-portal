Feature: Generic Register for new account, Login, Logout

  Scenario: Register for new account.
    Given the user accesses the url "/"
      Then I click on a link with class "new_account"
      Then I entered "user_register_email" with "test@mp.com"
      Then I entered "user_register_password" with "behave123"
      Then I entered "user_register_mobile" with "12542567890"
      Then I selected "user_register_current_city" with "1"
      Then I selected "user_register_technical_skills" with "1"
      Then I selected "user_register_technical_skills" with "2"
      Then I choose option "user_register_year" with "2"
      Then I choose option "user_register_month" with "5"
      Then I click on button with class "register_form_button"
      Then I submit form with id "ApplicantFormRegister"
    Given the user accesses the url "/user/reg_success/"

  Scenario: Logout User
    Given the user accesses the url "/logout/"

  Scenario: Login to an existing account.
    Given the user accesses the url "/"
      Then I click on a link with class "login_modal"
      Then I entered "userlogin_email" with "test@mp.com"
      Then I entered "userlogin_password" with "behave123"
      Then I click on button with class "login_form_button"
      Then I submit form with id "ApplicantForm"
    Given the user accesses the url "/user/reg_success/"
  
  Scenario: Logout User
    Given the user accesses the url "/logout/"

  Scenario: Forgot Password to an existing account.
    Given the user accesses the url "/"
      Then I click on a link with class "login_modal"
      Then I click on a div with id "forgot_pass"
      Then I entered "userlogin_email" with "test@mp.com"
      Then I click on button with class "login_form_button"
      Then I submit form with id "ApplicantForm"