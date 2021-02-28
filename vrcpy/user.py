from vrcpy.errors import ObjectErrors
from vrcpy.baseobject import BaseObject

import logging


class FriendStatus(BaseObject):
    def __init__(self, obj, user_id):
        super(None, None)

        self.required.update({
            "incoming_request": {
                "dict_key": "incomingRequest",
                "type": bool
            },
            "is_friend": {
                "dict_key": "isFriend",
                "type": bool
            },
            "outgoing_request": {
                "dict_key": "outgoingRequest",
                "type": bool
            }
        })

        self.user_id = user_id
        self._assign(obj)


class LimitedUser(BaseObject):
    def __init__(self, client, obj=None, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "username": {
                "dict_key": "username",
                "type": str
            },
            "display_name": {
                "dict_key": "displayName",
                "type": str
            },
            "id": {
                "dict_key": "id",
                "type": str
            },
            "avatar_image_url": {
                "dict_key": "currentAvatarImageUrl",
                "type": str
            },
            "avatar_thumbnail_url": {
                "dict_key": "currentAvatarThumbnailImageUrl",
                "type": str
            },
            "last_platform": {
                "dict_key": "last_platform",
                "type": str
            },
            "tags": {
                "dict_key": "tags",
                "type": list
            },
            "developer_type": {
                "dict_key": "developerType",
                "type": str
            },
            "is_friend": {
                "dict_key": "isFriend",
                "type": bool
            },
            "status_description": {
                "dict_key": "statusDescription",
                "type": str
            },
            "last_login": {
                "dict_key": "last_login",
                "type": str
            }
        })

        self.optional.update({
            "status": {
                "dict_key": "status",
                "type": str
            },
            "bio": {
                "dict_key": "bio",
                "type": str
            },
            "location": {
                "dict_key": "location",
                "type": str
            }
        })

        if obj is not None:
            self._assign(obj)

    async def fetch_full(self):
        '''
        Returns this user as a User object
        '''

        logging.info("Getting User object of user " + self.username)

        return await self.client.fetch_user_via_id(self.id)

    async def fetch_friend_status(self):
        '''
        Gets friend request and is_friend status'
        Returns FriendStatus object
        '''

        friend_status = await self.client.request.call(
            "/user/%s/friendStatus" % self.id)
        return FriendStatus(friend_status["data"], self.id)

    async def send_friend_request(self):
        '''
        Sends a friend request notification to this user
        '''

        logging.info("Sending friend request to " + self.username)

        if self.is_friend:
            raise ObjectErrors.AlreadyFriends(
                "You are already friends with " + self.display_name)

        await self.client.request.call(
            "/user/%s/friendRequest" % self.id, "POST")

    async def unfriend(self):
        '''
        Unfriends this user
        '''

        logging.info("Unfriending user " + self.username)

        if not self.is_friend:
            raise ObjectErrors.NotFriends(
                "You are not friends with " + self.display_name)

        await self.client.request.call(
            "/auth/user/friends/" + self.id, "DELETE")

    async def favorite(self, group):
        '''
        Favorite this user
        Returns a FriendFavorite object

            group, str
            Name of group to add friend to
        '''

        logging.info("Favoriting user with id " + self.id)

        if not self.is_friend:
            raise ObjectErrors.NotFriends(
                "You are not friends with " + self.display_name)

        if group not in self.client.me.friend_group_names:
            raise ObjectErrors.InvalidGroupName(
                "Group name must be one of %s, not %s" % (
                    self.client.me.friend_group_names,
                    group
                )
            )

        resp = await self.client.request.call(
            "/favorites",
            "POST",
            params={
                "type": "friend",
                "favoriteId": self.id,
                "tags": [group]
            }
        )

        return self.client._BaseFavorite.build_favorite(
            self.client, resp["data"], self.loop)

    async def add_moderation(self, t):
        '''
        Adds a moderation against this user
        Returns a PlayerModeration

            t, str (use enum.PlayerModerationType for convenience)
            Type of moderation
        '''

        moderation = await self.client._PlayerModeration.create_moderation(
            t, self.id, self.client, self.loop
        )

        return moderation


class User(LimitedUser):
    def __init__(self, client, obj=None, loop=None):
        super().__init__(client, loop=loop)

        '''
        self.required.update({

        })
        '''

        self.optional.update({
            "bio_links": {
                "dict_key": "bioLinks",
                "type": list
            },
            "state": {
                "dict_key": "state",
                "type": str
            },
            "friend_key": {
                "dict_key": "friendKey",
                "type": str
            },
            "world_id": {
                "dict_key": "worldId",
                "type": str
            },
            "instance_id": {
                "dict_key": "instanceId",
                "type": str
            },
            "allow_avatar_copying": {
                "dict_key": "allowAvatarCopying",
                "type": bool
            }
        })

        if obj is not None:
            self._assign(obj)


class CurrentUser(User):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "past_display_names": {
                "dict_key": "pastDisplayNames",
                "type": list
            },
            "email_verified": {
                "dict_key": "emailVerified",
                "type": bool
            },
            "has_email": {
                "dict_key": "hasEmail",
                "type": bool
            },
            "has_pending_email": {
                "dict_key": "hasPendingEmail",
                "type": bool
            },
            "accepted_tos_version": {
                "dict_key": "acceptedTOSVersion",
                "type": int
            },
            "has_birthday": {
                "dict_key": "hasBirthday",
                "type": bool
            },
            "friends": {
                "dict_key": "friends",
                "type": list
            },
            "online_friends": {
                "dict_key": "onlineFriends",
                "type": list
            },
            "active_friends": {
                "dict_key": "activeFriends",
                "type": list
            },
            "offline_friends": {
                "dict_key": "offlineFriends",
                "type": list
            },
            "friend_group_names": {
                "dict_key": "friendGroupNames",
                "type": list
            },
            "avatar": {
                "dict_key": "currentAvatar",
                "type": dict
            },
            "avatar_asset_url": {
                "dict_key": "currentAvatarAssetUrl",
                "type": str
            },
            "home_location": {
                "dict_key": "homeLocation",
                "type": str
            },
            "has_logged_in_from_client": {
                "dict_key": "hasLoggedInFromClient",
                "type": bool
            },
            "mfa_enabled": {
                "dict_key": "twoFactorAuthEnabled",
                "type": bool
            },
            "unsubscribe": {
                "dict_key": "unsubscribe",
                "type": bool
            },
            "feature": {
                "dict_key": "feature",
                "type": dict
            }
        })

        self.optional.update({
            "email": {
                "dict_key": "email",
                "type": str
            },
            "obfuscated_email": {
                "dict_key": "obfuscatedEmail",
                "type": str
            },
            "obfuscated_pending_email": {
                "dict_key": "obfuscatedPendingEmail",
                "type": str
            },
            "steam_id": {
                "dict_key": "steamId",
                "type": str
            },
            "steam_details": {
                "dict_key": "steamDetails",
                "type": dict
            },
            "oculus_id": {
                "dict_key": "oculusId",
                "type": str
            },
            "account_deletion_date": {
                "dict_key": "accountDeletionDate",
                "type": str
            }
        })

        self._assign(obj)

    async def fetch_friends(self):
        '''
        Returns list of LimitedUser objects
        '''

        logging.info("Fetching friends")

        friends = []

        for offset in range(
                0,
                len(self.online_friends) + len(self.offline_friends),
                100):

            resp = await self.client.request.call(
                "/auth/user/friends", params={
                    "offset": offset,
                    "n": 100,
                    "offline": False})

            for user in resp["data"]:
                friends.append(LimitedUser(self.client, user, self.loop))

        for offset in range(0, len(self.offline_friends), 100):
            resp = await self.client.request.call(
                "/auth/user/friends", params={
                    "offset": offset,
                    "n": 100,
                    "offline": True})

            for user in resp["data"]:
                friends.append(LimitedUser(self.client, user, self.loop))

        return friends
