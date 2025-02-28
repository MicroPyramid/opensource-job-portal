from jobsp.celery import app
from mpcomp.facebook import GraphAPI
import requests
from django.conf import settings
from peeldb.models import (
    User,
    FacebookFriend,
    FacebookPage,
    FacebookGroup,
    TwitterFollower,
    TwitterFriend,
)


@app.task()
def add_twitter_friends_followers(user_id, friends, followers):
    """
    getting the user object
    Removing twitter followers, friends if the user previously connected to twitter
    Creating followers, friends from followers, friends list
    """
    user = User.objects.filter(id=user_id).first()
    TwitterFollower.objects.filter(user=user).delete()
    for i in followers["users"]:
        TwitterFollower.objects.create(
            user=user, twitter_id=i["id"], screen_name=i["screen_name"]
        )

    TwitterFriend.objects.filter(user=user).delete()
    for i in friends["users"]:
        TwitterFriend.objects.create(
            user=user, twitter_id=i["id"], screen_name=i["screen_name"]
        )


# @app.task()
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


@app.task()
def facebook_friends(accesstoken, user):
    user = User.objects.filter(id=user).first()
    """
        1. getting the graph object by using the accesstoken
        2. getting the frieds list from graph object
        3. Removing friends data if the user previously connected to the site
        4. Creating facebook friends list
    """

    graph = GraphAPI(accesstoken)
    friends = graph.get_object("me/friends")
    FacebookFriend.objects.filter(user=user).delete()
    for each in friends["data"]:
        FacebookFriend.objects.create(
            user=user, facebook_id=each["id"], name=each["name"]
        )


@app.task()
def facebook_pages(accesstoken, user):
    user = User.objects.filter(id=user).first()
    """
        1. sending the get request to facebook graph api with the user accesstoken
        2. getting the pages list from graph object
        3. Removing fb pages data if the user previously connected to the site
        4. Creating facebook pages list with the page accesstoken
    """

    fb_pages = requests.get(
        "https://graph.facebook.com/me/accounts", params={"access_token": accesstoken}
    )
    pages = fb_pages.json()["data"]
    FacebookPage.objects.filter(user=user).delete()
    for each in pages:
        FacebookPage.objects.create(
            user=user,
            category=each["category"],
            accesstoken=accesstoken,
            name=each["name"],
            page_id=each["id"],
            permission=each["perms"],
        )


@app.task()
def facebook_groups(accesstoken, user):
    user = User.objects.filter(id=user).first()
    """
        1. sending the get request to facebook graph api with the user accesstoken
        2. getting the groups list from graph object
        3. Removing fb groups data if the user previously connected to the site
        4. Creating facebook groups list with the page accesstoken
    """

    fb_groups = requests.get(
        "https://graph.facebook.com/me/groups", params={"access_token": accesstoken}
    )
    groups = fb_groups.json()["data"]
    FacebookGroup.objects.filter(user=user).delete()
    for group in groups:
        FacebookGroup.objects.create(
            user=user, group_id=group["id"], name=group["name"]
        )

