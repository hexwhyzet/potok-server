# import base64
# import logging
# from typing import List
#
# from django.http import JsonResponse, HttpResponseNotFound
# from django.shortcuts import render
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
#
# from potok_app.config import Secrets, Config
# from potok_app.functions import is_valid_url, does_contain_only_letters_numbers_underscores
# from potok_app.importer import pics_json_parser, profiles_json_parser
# from potok_app.models import Picture, Profile, PictureLike, Subscription, Comment, CommentLike, ProfileSuggestion, \
#     NAME_MAX_LENGTH, SCREEN_NAME_MAX_LENGTH, ProfileAttachment
# from potok_app.services import create_session, session_by_token
# from potok_app.services import link_by_share_token, share_token_by_link, create_picture_link
# from potok_app.services import profile_by_id, search_profiles_by_screen_name_prefix, search_profiles_by_text, \
#     avatar_url, switch_block, is_profile_content_available, are_liked_pictures_available, is_blocked_by_user, \
#     is_profile_users, \
#     update_name, does_screen_name_exists, update_screen_name, update_publicity, update_liked_pictures_publicity, \
#     add_avatar, trending_profiles
# from potok_app.services import subscription_pictures, feed_pictures, profile_pictures, \
#     picture_by_id, liked_pictures, high_resolution_url, mid_resolution_url, low_resolution_url, add_picture, \
#     picture_can_be_deleted_by_user, delete_picture, add_report
# from potok_app.services import switch_like, last_actions, add_view, switch_subscription, comment_by_id, \
#     add_comment, comments_of_picture, switch_like_comment, comment_can_be_deleted_by_user, delete_comment, unsubscribe
# from potok_users.authorizer import get_user_profile
#
# secrets = Secrets()
# config = Config()
#
# logger = logging.getLogger(__name__)
from django.http import Http404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from potok_app.api.pictures.serializers import SizesMixin
from potok_app.models import Picture
from potok_app.services.share.share import get_share_by_token, does_share_exist


class ShareView(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, token):
        if not does_share_exist(token):
            raise Http404
        share = get_share_by_token(token)
        if isinstance(share.content_object, Picture):
            picture: Picture = share.content_object
            sizes = SizesMixin().get_sizes(picture)
            return Response({'picture_url': sizes[-1]['url']}, template_name='share/picture.html')
        raise Http404

# def construct_app_response(status, content):
#     response = {
#         "status": status,
#         "content": content,
#     }
#     return JsonResponse(response)
#
#
# def construct_picture_response(pic: Picture, user_profile: Profile = None):
#     response_content = {
#         "id": pic.id,
#         "type": "picture",
#         "low_res_url": f"{config['image_server_url']}/{config['image_server_bucket']}{low_resolution_url(pic)}",
#         "mid_res_url": f"{config['image_server_url']}/{config['image_server_bucket']}{mid_resolution_url(pic)}",
#         "high_res_url": f"{config['image_server_url']}/{config['image_server_bucket']}{high_resolution_url(pic)}",
#         "date": pic.date,
#         "views_num": pic.views_num,
#         "likes_num": pic.likes_num,
#         "comments_num": Comment.objects.filter(picture=pic).count(),
#         "shares_num": pic.shares_num,
#         "is_liked": pic.profiles_liked.filter(id=user_profile.id).exists() if user_profile is not None else None,
#         "like_url": f"{config['main_server_url']}/app/like_picture/{pic.id}",
#         "share_url": f"{config['main_server_url']}/app/share_picture/{pic.id}",
#         "add_comment_url": f"{config['main_server_url']}/app/add_comment/{pic.id}",
#         "profile": construct_profile_response(pic.profile, user_profile),
#         "link_url": pic.link_url,
#         "report_url": f"{config['main_server_url']}/app/report_picture/{pic.id}",
#         "delete_url": f"{config['main_server_url']}/app/delete_picture/{pic.id}",
#         "can_be_deleted": picture_can_be_deleted_by_user(user_profile, pic),
#         "text": pic.text,
#     }
#     return response_content
#
#
# def construct_pictures(pictures: list[Picture], user_profile: Profile = None):
#     pictures = [construct_picture_response(picture, user_profile) for picture in pictures]
#     return pictures
#
#
# def construct_profile_response(profile: Profile, user_profile: Profile = None):
#     is_users = is_profile_users(user_profile, profile)
#     response_content = {
#         "id": profile.id,
#         "type": "profile",
#         "is_public": profile.is_public,
#         "are_liked_pictures_public": profile.are_liked_pictures_public,
#         "is_user_blocked_by_you": is_blocked_by_user(user_profile, profile) if user_profile is not None else None,
#         "are_you_blocked_by_user": is_blocked_by_user(profile, user_profile) if user_profile is not None else None,
#         "is_profile_available": is_profile_content_available(user_profile,
#                                                              profile) if user_profile is not None else None,
#         "are_liked_pictures_available": are_liked_pictures_available(user_profile,
#                                                                      profile) if user_profile is not None else None,
#         "name": profile.name or "No name",
#         "profile_attachments": construct_attachments(profile.profile_attachments.all()),
#         "screen_name": profile.screen_name or "unknown",
#         "description": profile.description or None,
#         "subs_num": profile.subs_num if user_profile is not None else None,
#         "followers_num": profile.followers_num,
#         "views_num": profile.views_num,
#         "likes_num": profile.likes_num,
#         "avatar_url": f"{config['image_server_url']}/{config['image_server_bucket']}{avatar_url(profile) or '/defaults/avatar.png'}",
#         "is_subscribed": user_profile.subs.filter(id=profile.id).exists() if user_profile is not None else False,
#         "subscribe_url": f"{config['main_server_url']}/app/subscribe/{profile.id}" if not is_users else None,
#         "share_url": f"{config['main_server_url']}/app/share_profile/{profile.id}",
#         "block_url": f"{config['main_server_url']}/app/block_profile/{profile.id}" if not is_users else None,
#         "is_yours": is_users,
#         "reload_url": f"{config['main_server_url']}/app/profile/{profile.id}",
#     }
#     return response_content
#
#
# def construct_attachment(attachment: ProfileAttachment):
#     response_content = {
#         "type": "attachment",
#         "tag": attachment.tag,
#         "url": attachment.url,
#     }
#     return response_content
#
#
# def construct_attachments(profile_attachments: List[ProfileAttachment]):
#     return list(map(construct_attachment, profile_attachments))
#
#
# def construct_profiles(profiles: list[Profile], user_profile: Profile = None):
#     constructed_profiles = [construct_profile_response(profile, user_profile) for profile in profiles]
#     return constructed_profiles
#
#
# def construct_subscription_response(user_profile: Profile, subscription: Subscription):
#     response_content = {
#         "type": "subscriptions",
#         "profile": construct_profile_response(subscription.follower, user_profile),
#         "date": int(subscription.date.timestamp()),
#     }
#     return response_content
#
#
# def construct_like_response(user_profile: Profile, like: PictureLike):
#     response_content = {
#         "type": "like",
#         "profile": construct_profile_response(like.profile, user_profile),
#         "picture": construct_picture_response(like.picture, user_profile),
#         "date": int(like.date.timestamp()),
#     }
#     return response_content
#
#
# def construct_comment_response(comment: Comment, user_profile: Profile):
#     response_content = {
#         "type": "comment",
#         "id": comment.id,
#         "profile": construct_profile_response(comment.profile, user_profile),
#         "picture": construct_picture_response(comment.picture, user_profile),
#         "text": comment.text,
#         "like_url": f"{config['main_server_url']}/app/like_comment/{comment.id}",
#         "likes_num": comment.likes_num,
#         "is_liked": CommentLike.objects.filter(profile=user_profile, comment=comment).exists(),
#         "is_liked_by_creator": CommentLike.objects.filter(profile=comment.profile, comment=comment).exists(),
#         "date": int(comment.date.timestamp()),
#         "can_be_deleted": comment_can_be_deleted_by_user(user_profile, comment),
#         "delete_url": f"{config['main_server_url']}/app/delete_comment/{comment.id}",
#     }
#     return response_content
#
#
# def construct_ads_response():
#     response_content = {
#         "type": "ads",
#     }
#     return response_content
#
#
# def construct_comments(user_profile: Profile, comments: list[Comment]):
#     constructed_comments = [construct_comment_response(comment, user_profile) for comment in comments]
#     return constructed_comments
#
#
# def construct_action(user_profile, action):
#     if isinstance(action, PictureLike):
#         return construct_like_response(user_profile, action)
#     elif isinstance(action, Subscription):
#         return construct_subscription_response(user_profile, action)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_create_session_request(request, user_profile):
#     session = create_session(user_profile)
#     response_content = {
#         "session_token": session.token,
#     }
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_subscription_pictures(request, user_profile, session_token, number):
#     session = session_by_token(session_token)
#     pictures = subscription_pictures(user_profile, session, number)
#     response_content = construct_pictures(pictures, user_profile)
#     # if len(response_content) > 0:
#     #     response_content += [construct_ads_response()]
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_feed_pictures(request, user_profile, session_token, number):
#     session = session_by_token(session_token)
#     pictures = feed_pictures(user_profile, session, number)
#     response_content = construct_pictures(pictures, user_profile)
#     # if len(response_content) > 0:
#     #     response_content += [construct_ads_response()]
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_my_profile(request, user_profile):
#     response_content = construct_profile_response(user_profile, user_profile)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_profile_pictures(request, user_profile, profile_id, number=10, offset=0):
#     pictures = profile_pictures(profile_id, number, offset)
#     response_content = construct_pictures(pictures, user_profile)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_liked_pictures(request, user_profile, profile_id, number=10, offset=0):
#     profile = profile_by_id(profile_id)
#     if (profile == user_profile) or \
#             (profile.are_liked_videos_public and (profile.is_public or are_fiends(profile, user_profile))):
#         pictures = liked_pictures(profile_id, number, offset)
#         response_content = construct_pictures(pictures, user_profile)
#         return construct_app_response(200, response_content)
#     else:
#         return construct_app_response("liked pictures are private", None)
#
#
# @api_view(['POST'])
# @get_user_profile
# def app_add_picture(request, user_profile):
#     picture_data = base64.b64decode(request.POST["picture"])
#     link = request.POST["link"]
#     if len(link.strip()) != 0:
#         if not (is_valid_url(link)):
#             return construct_app_response("error", "Url is invalid")
#     else:
#         link = None
#     add_picture(user_profile, picture_data, request.POST["extension"], link)
#     return construct_app_response(200, None)
#
#
# @api_view(['POST'])
# @get_user_profile
# def app_add_avatar(request, user_profile):
#     avatar_data = base64.b64decode(request.POST["avatar"])
#     add_avatar(user_profile, avatar_data, request.POST["extension"])
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_switch_like(request, user_profile, picture_id):
#     picture = picture_by_id(picture_id)
#     switch_like(user_profile, picture)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_delete_picture(request, user_profile, picture_id):
#     picture = picture_by_id(picture_id)
#     if picture_can_be_deleted_by_user(user_profile, picture):
#         delete_picture(picture)
#         return construct_app_response(200, None)
#
#     return construct_app_response("Picture can't be deleted", None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_switch_subscription(request, user_profile, sub_profile_id):
#     sub_profile = profile_by_id(profile_id=sub_profile_id)
#     switch_subscription(user_profile, sub_profile)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_add_view(request, user_profile, picture_id):
#     add_view(user_profile, picture_by_id(picture_id))
#     return construct_app_response(200, None)
#
#
# # @api_view(['GET'])
# # @get_user_profile
# # def app_generate_profile_share_link(request, user_profile, profile_id):
# #     profile = profile_by_id(profile_id)
# #     link = create_link(user_profile, profile)
# #     share_token = share_token_by_link(link)
# #     response_content = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
# #     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_generate_picture_share_link(request, user_profile, picture_id):
#     picture = picture_by_id(picture_id)
#     link = create_picture_link(user_profile, picture)
#     share_token = share_token_by_link(link)
#     response_content = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_last_actions(request, user_profile, number, offset):
#     actions = last_actions(user_profile, number, offset)
#     response_content = [construct_action(user_profile, action) for action in actions]
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_autofill(request, user_profile, search_string, number, offset):
#     profiles = search_profiles_by_screen_name_prefix(search_string, number, offset)
#     response_content = construct_profiles(profiles, user_profile)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_search(request, user_profile, search_string, number, offset):
#     profiles = search_profiles_by_text(search_string, number, offset)
#     response_content = construct_profiles(profiles, user_profile)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_like_comment(request, user_profile, comment_id):
#     comment = comment_by_id(comment_id)
#     switch_like_comment(profile=user_profile, comment=comment)
#     return construct_app_response(200, None)
#
#
# @api_view(['POST'])
# @get_user_profile
# def app_add_comment(request, user_profile, picture_id):
#     text = request.POST["content"]
#     picture = picture_by_id(picture_id)
#     add_comment(profile=user_profile, picture=picture, text=text)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_delete_comment(request, user_profile, comment_id):
#     comment = comment_by_id(comment_id)
#     if comment_can_be_deleted_by_user(user_profile, comment):
#         delete_comment(comment)
#         return construct_app_response(200, None)
#
#     return construct_app_response("Comment can't be deleted", None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_picture_comments(request, user_profile, picture_id, number, offset):
#     picture = picture_by_id(picture_id)
#     comments = comments_of_picture(picture, number, offset)
#     comments = list(sorted(sorted(comments, key=lambda comment: comment.likes_num, reverse=True),
#                            key=lambda comment: comment.profile == user_profile, reverse=True))
#     response_content = construct_comments(user_profile, comments)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_block_profile(request, user_profile, profile_id):
#     block_profile = profile_by_id(profile_id)
#     unsubscribe(user_profile, block_profile)
#     unsubscribe(block_profile, user_profile)
#     if user_profile == block_profile:
#         return construct_app_response("You cannot block yourself", None)
#
#     switch_block(user_profile, block_profile)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_report_picture(request, user_profile, picture_id):
#     picture = picture_by_id(picture_id)
#     add_report(user_profile, picture)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_profile(request, user_profile, profile_id):
#     profile = profile_by_id(profile_id)
#     response_content = construct_profile_response(profile, user_profile)
#     return construct_app_response(200, response_content)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_change_setting(request, user_profile: Profile, setting_name, new_value):
#     if setting_name == "screen_name":
#         if len(new_value) > SCREEN_NAME_MAX_LENGTH:
#             return construct_app_response(f"Username should be shorter than {NAME_MAX_LENGTH} letters", None)
#         if not does_contain_only_letters_numbers_underscores(new_value):
#             return construct_app_response("Only letters, numbers, underscores are allowed", None)
#         if does_screen_name_exists(new_value):
#             return construct_app_response("The username is already taken", None)
#         update_screen_name(user_profile, new_value)
#         return construct_app_response(200, None)
#     elif setting_name == "name":
#         if len(new_value) > NAME_MAX_LENGTH:
#             return construct_app_response("error", f"Name should be shorter than {NAME_MAX_LENGTH} letters")
#         update_name(user_profile, new_value)
#         return construct_app_response(200, None)
#     elif setting_name == "is_public":
#         if str(new_value) == "0":
#             update_publicity(user_profile, False)
#         else:
#             update_publicity(user_profile, True)
#         return construct_app_response(200, None)
#     elif setting_name == "are_liked_pictures_public":
#         if str(new_value) == "0":
#             update_liked_pictures_publicity(user_profile, False)
#         else:
#             update_liked_pictures_publicity(user_profile, True)
#         return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @get_user_profile
# def app_trending(request, user_profile, number, offset):
#     profiles = trending_profiles(number, offset)
#     response = construct_profiles(profiles, user_profile)
#     return construct_app_response(200, response)
#
#
# @api_view(['POST'])
# @get_user_profile
# def app_suggest_profile(request, user_profile):
#     url = request.POST["content"]
#     if not is_valid_url(url):
#         return construct_app_response("error", "Url is invalid")
#
#     ProfileSuggestion.objects.create(profile=user_profile, content=url)
#     return construct_app_response(200, None)
#
#
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_error():
#     res = 1 / 0
#     return construct_app_response(200, "Success")
#
#
# def update_pictures_db(request):
#     post_json = request.POST["archive"]
#     pics_json_parser(post_json)
#     return construct_app_response(200, None)
#
#
# def update_profiles_db(request):
#     post_json = request.POST["archive"]
#     profiles_json_parser(post_json)
#     return construct_app_response(200, None)
#
#
# def index_page(request):
#     return render(request, 'index.html')
#
#
# def content_by_link(request, share_token: str):
#     link = link_by_share_token(share_token)
#     if isinstance(link.content, Picture):
#         response_content = construct_picture_response(link.content)
#         return render(request, 'share.html', {"picture": response_content})
#     elif isinstance(link.content, Profile):
#         response_content = construct_profile_response(link.content)
#         return construct_app_response(200, response_content)
#     else:
#         return HttpResponseNotFound("Meme not Found :(")
