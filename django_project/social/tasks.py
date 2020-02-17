from celery.task import task
from mpcomp.facebook import GraphAPI
import celery
import requests
from django.conf import settings
from peeldb.models import (User, GoogleFirend, FacebookFriend, FacebookPage, FacebookGroup,
                           TwitterFollower, TwitterFriend)
from mpcomp import gauth, contacts


@task()
def add_twitter_friends_followers(user_id, friends, followers):

    '''
        getting the user object
        Removing twitter followers, friends if the user previously connected to twitter
        Creating followers, friends from followers, friends list
    '''
    user = User.objects.filter(id=user_id).first()
    TwitterFollower.objects.filter(user=user).delete()
    for i in followers['users']:
        TwitterFollower.objects.create(
            user=user, twitter_id=i['id'], screen_name=i['screen_name'])

    TwitterFriend.objects.filter(user=user).delete()
    for i in friends['users']:
        TwitterFriend.objects.create(
            user=user, twitter_id=i['id'], screen_name=i['screen_name'])


# @celery.task()
# def facebook_information(accesstoken, profile, hometown, bday, location, user):
#     '''
#         creating a facebook object with all facebook profile information
#     '''

#     Facebook.objects.create(
#         user=user,
#         facebook_url=profile['link'],
#         facebook_id=profile['id'],
#         first_name=profile['first_name'],
#         last_name=profile['last_name'],
#         verified=profile['verified'],
#         name=profile['name'],
#         language=profile['locale'],
#         hometown=hometown,
#         email=profile['email'],
#         gender=profile['gender'],
#         dob=bday,
#         location=location,
#         timezone=profile['timezone'],
#         accesstoken=accesstoken
#     )


@celery.task()
def facebook_friends(accesstoken, user):
    user = User.objects.filter(id=user).first()
    '''
        1. getting the graph object by using the accesstoken
        2. getting the frieds list from graph object
        3. Removing friends data if the user previously connected to the site
        4. Creating facebook friends list
    '''

    graph = GraphAPI(accesstoken)
    friends = graph.get_object("me/friends")
    FacebookFriend.objects.filter(user=user).delete()
    for each in friends['data']:
        FacebookFriend.objects.create(
            user=user, facebook_id=each['id'], name=each['name'])


@celery.task()
def facebook_pages(accesstoken, user):
    user = User.objects.filter(id=user).first()
    '''
        1. sending the get request to facebook graph api with the user accesstoken
        2. getting the pages list from graph object
        3. Removing fb pages data if the user previously connected to the site
        4. Creating facebook pages list with the page accesstoken
    '''

    fb_pages = requests.get(
        "https://graph.facebook.com/me/accounts", params={'access_token': accesstoken})
    pages = fb_pages.json()['data']
    FacebookPage.objects.filter(user=user).delete()
    for each in pages:
        FacebookPage.objects.create(user=user, category=each['category'],
                                    accesstoken=accesstoken, name=each['name'],
                                    page_id=each['id'], permission=each['perms'])


@celery.task()
def facebook_groups(accesstoken, user):
    user = User.objects.filter(id=user).first()
    '''
        1. sending the get request to facebook graph api with the user accesstoken
        2. getting the groups list from graph object
        3. Removing fb groups data if the user previously connected to the site
        4. Creating facebook groups list with the page accesstoken
    '''

    fb_groups = requests.get(
        "https://graph.facebook.com/me/groups", params={'access_token': accesstoken})
    groups = fb_groups.json()['data']
    FacebookGroup.objects.filter(user=user).delete()
    for group in groups:
        FacebookGroup.objects.create(
            user=user, group_id=group['id'], name=group['name'])


@celery.task()
def add_google_friends(user_id, accesstoken):
    '''
        1. Getting the user object
        2. Getting the gdata autok token by sending google app id, secret id
        3. Retrieving the accesstoken
        4. Getting the conacts object which returns 3000 objects maximum
        4. Creating google friends list with the xml page response
    '''

    user = User.objects.filter(id=user_id).first()
    auth_token = gauth.OAuth2Token(
        client_id=settings.GP_CLIENT_ID,
        client_secret=settings.GP_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email ' +
              'https://www.googleapis.com/auth/contacts.readonly ',
        user_agent='dummy-sample'
    )

    auth_token.access_token = accesstoken
    client1 = contacts.ContactsClient(source='')
    client1 = auth_token.authorize(client1)
    qry = contacts.ContactsQuery(max_results=3000)
    feed = client1.get_contacts(query=qry)
    for each in [feed]:
        each_feed = [each][0]
        friend_id = each_feed.id.text
        entry = [each][0].entry
        for each_entry in [entry]:
            for entry in each_entry:
                fullname = email = familyname = ''
                if entry.name is not None:
                    if entry.name.full_name is not None:
                        fullname = entry.name.full_name.text
                    if entry.name.family_name is not None:
                        familyname = entry.name.family_name.text
                if entry.email:
                    email = entry.email[0].address
                    if not GoogleFirend.objects.filter(user=user, email=email):
                        GoogleFirend.objects.create(
                            user=user,
                            friend_id=friend_id,
                            fullname=fullname,
                            title='',
                            email=email,
                            phone='',
                            familyname=familyname
                        )
