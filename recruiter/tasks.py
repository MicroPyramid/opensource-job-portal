import requests

from jobsp.celery import app
from django.conf import settings
from twython.api import Twython

from mpcomp.facebook import GraphAPI
from mpcomp import gauth, contacts
from peeldb.models import (
    User,
    TwitterFollower,
    TwitterFriend,
    FacebookFriend,
    FacebookPage,
    FacebookGroup,
    Facebook,
    Twitter,
    FacebookPost,
    TwitterPost,
)


@app.task()
def add_twitter_friends_followers(user_id, friends, followers):

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


@app.task()
def add_facebook_friends_pages_groups(accesstoken, fid, user):
    graph = GraphAPI(accesstoken)
    friends = graph.get_object("me/friends")
    # TODO:
    # Facebook not giving all friends, we need to frinds in paging and insert.
    for friend in friends["data"]:
        FacebookFriend.objects.create(
            user=user, name=friend["name"], facebook_id=friend["id"]
        )
    user_profile = requests.get(
        "https://graph.facebook.com/me/accounts", params={"access_token": accesstoken}
    )
    pages = user_profile.json()["data"]

    for page in pages:
        url = (
            "https://graph.facebook.com/oauth/access_token?client_id="
            + settings.FB_APP_ID
            + "&client_secret="
            + settings.FB_SECRET
            + "&grant_type=fb_exchange_token&fb_exchange_token="
            + accesstoken
        )
        import urllib.request as ur

        print(ur.urlopen(url).read())
        response = str(ur.urlopen(url).readline()).split("&")[0]
        if len(response.split("=")) > 2:
            access_token = response.split("=")[1]

            FacebookPage.objects.create(
                user=user,
                category=page["category"],
                name=page["name"],
                accesstoken=access_token,
                page_id=page["id"],
                permission=page["perms"],
            )

    user_groups = requests.get(
        "https://graph.facebook.com/me/groups", params={"access_token": accesstoken}
    )
    groups = user_groups.json()["data"]
    for group in groups:
        FacebookGroup.objects.create(
            user=user, group_id=group["id"], name=group["name"]
        )


@app.task()
def del_jobpost_tw(user, post):
    user = User.objects.filter(id=user).first()
    if user:
        user_twitter = Twitter.objects.filter(user=user).first()
        twitter = Twython(
            settings.TW_APP_KEY,
            settings.TW_APP_SECRET,
            user_twitter.oauth_token,
            user_twitter.oauth_secret,
        )
        try:
            twitter.destroy_status(id=post.post_id)
            post = TwitterPost.objects.filter(id=post)
            post.delete()
        except:
            print("not deleted")
    else:
        return "connect to twitter"


@app.task()
def del_jobpost_peel_fb(user, post):
    user = User.objects.filter(id=user).first()
    if user:
        try:
            graph = GraphAPI(settings.REC_FB_ACCESS_TOKEN)
            post = FacebookPost.objects.filter(id=post).first()
            post.post_status = "Deleted"
            post.save()
            graph.delete_object(post.post_id)
        except:
            print("not deleted")
        return "deleted successfully"
    return "connect to fb"


@app.task()
def del_jobpost_fb(user, post):
    user = User.objects.filter(id=user).first()
    if user:
        try:
            graph = GraphAPI(Facebook.objects.get(user=user).accesstoken)
            post = FacebookPost.objects.filter(id=post).first()
            post.post_status = "Deleted"
            post.save()
            graph.delete_object(post.post_id)
        except:
            print("not deleted")
        return "deleted successfully"
    return "connect to fb"
