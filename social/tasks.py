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

