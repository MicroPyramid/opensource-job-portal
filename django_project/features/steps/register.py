import time

@then(u'I entered "{field}" with "{value}"')
def fill_in_the_field(context, field, value):
    context.browser.find_by_id(field).fill(value)

@then(u'I click on a link with class "{name}"')
def click_on_link(context, name):
    context.browser.find_by_xpath('//a[@class="'+ name +'"]')[0].click()

@then(u'I click on a div with id "{name}"')
def click_on_link(context, name):
    context.browser.find_by_xpath('//div[@id="'+ name +'"]')[0].click()

@then(u'I selected "{field}" with "{value}"')
def selecting_values(context, field, value):
    context.browser.find_by_xpath('//select[@id="'+ field +'"]//option[@value="'+ value +'"]')[0].click()

@then(u'I choose option "{field}" with "{value}"')
def selecting_values(context, field, value):
    context.browser.execute_script("document.getElementById('"+field+"').value='"+value+"'")

@then(u'I click on button with class "{name}"')
def click_on_button(context, name):
    context.browser.find_by_xpath('//button[contains(@class, '+ name +')]')[0].click()

@then(u'I submit form with id "{name}"')
def submit_form(context, name):
    context.browser.execute_script("$('form#"+name+"').submit()")
    time.sleep(5)

@given(u'the user accesses the url "{url}"')
def open_page(context, url):
    context.browser.visit(context.server_url + url)