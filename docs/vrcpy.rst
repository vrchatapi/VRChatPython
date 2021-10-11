.. currentmodule:: vrcpy

API Reference
=============

Client
~~~~~~~

.. autoclass:: vrcpy.Client
    :members:
    :exclude-members: on_connect, on_ready, on_disconnect, on_friend_online, on_friend_offline, on_friend_active, on_friend_add, on_friend_delete, on_friend_update, on_friend_location, on_notification_received, on_notification_seen, on_notification_response, event, fetch_me, search_users, fetch_user, fetch_user_via_username, logout, verify_auth, user_exists

    .. automethod:: vrcpy.Client.fetch_me()
    .. automethod:: vrcpy.Client.search_users(search: str, developer_type: vrcpy.types.enum.DeveloperType = None, n: int = 60, offset: int = 0) -> list[vrcpy.user.User]
    .. automethod:: vrcpy.Client.fetch_user(id: str) -> vrcpy.user.User
    .. automethod:: vrcpy.Client.fetch_user_via_username(username: str) -> vrcpy.user.User
    .. automethod:: vrcpy.Client.logout(unauth: bool = True)
    .. automethod:: vrcpy.Client.verify_auth() -> dict[str, Union[bool, str]]
    .. automethod:: vrcpy.Client.user_exists(email: str = None, display_name: str = None, id: str = None, exclude_id: str = None) -> bool
    .. autodecorator:: vrcpy.Client.event

Events
~~~~~~~

.. automethod:: vrcpy.Client.on_connect
.. automethod:: vrcpy.Client.on_ready
.. automethod:: vrcpy.Client.on_disconnect
.. automethod:: vrcpy.Client.on_friend_online
.. automethod:: vrcpy.Client.on_friend_active
.. automethod:: vrcpy.Client.on_friend_offline
.. automethod:: vrcpy.Client.on_friend_add
.. automethod:: vrcpy.Client.on_friend_delete
.. automethod:: vrcpy.Client.on_friend_update
.. automethod:: vrcpy.Client.on_friend_location
.. automethod:: vrcpy.Client.on_notification_received
.. automethod:: vrcpy.Client.on_notification_seen
.. automethod:: vrcpy.Client.on_notification_response


User
~~~~~

.. _vrcpy.limiteduser.LimitedUser:
.. autoclass:: vrcpy.limiteduser.LimitedUser
    :no-members:

    .. automethod:: vrcpy.limiteduser.LimitedUser.moderate(typeof: vrcpy.types.enum.PlayerModerationType) -> vrcpy.moderation.Moderation
    .. automethod:: vrcpy.limiteduser.LimitedUser.unmoderate(typeof: vrcpy.types.enum.PlayerModerationType)
    .. automethod:: vrcpy.limiteduser.LimitedUser.unfriend()
    .. automethod:: vrcpy.limiteduser.LimitedUser.friend() -> vrcpy.notification.Notification
    .. automethod:: vrcpy.limiteduser.LimitedUser.cancel_friend()
    .. automethod:: vrcpy.limiteduser.LimitedUser.fetch_friend_status() -> dict[str, bool]

.. _vrcpy.user.User:
.. autoclass:: vrcpy.user.User
    :show-inheritance:
    :no-members:
    :inherited-members:

.. _vrcpy.currentuser.CurrentUser:
.. autoclass:: vrcpy.currentuser.CurrentUser
    :show-inheritance:
    :no-members:

    .. automethod:: vrcpy.currentuser.CurrentUser.fetch_friends(offset: int = 0, n: int = 60, offline: bool = False) -> list[vrcpy.limiteduser.LimitedUser]
    .. automethod:: vrcpy.currentuser.CurrentUser.fetch_player_moderations(id: str = None, typeof: vrcpy.types.enum.PlayerModerationType = None) -> list[vrcpy.moderation.Moderation]
    .. automethod:: vrcpy.currentuser.CurrentUser.fetch_moderation(id: str) -> vrcpy.moderation.Moderation
    .. automethod:: vrcpy.currentuser.CurrentUser.clear_player_moderations()
    .. automethod:: vrcpy.currentuser.CurrentUser.fetch_notifications(typeof: Union[vrcpy.types.enum.NotificationType, vrcpy.types.enum.SearchGenericType] = vrcpy.types.enum.SearchGenericType.ALL, hidden: bool = False, after: str = None, n: int = 60, offset: int = 0) -> list[vrcpy.notification.Notification]
    .. automethod:: vrcpy.currentuser.CurrentUser.fetch_notification(id: str) -> vrcpy.notification.Notification
    .. automethod:: vrcpy.currentuser.CurrentUser.clear_notifications()
    .. automethod:: vrcpy.currentuser.CurrentUser.update(email: str = None, birthday: str = None, accepted_tos_version: int = None, tags: list[str] = None, status: vrcpy.types.enum.UserStatus = None, status_description: str = None, bio: str = None, bio_links: list[str] = None, user_icon: str = None) -> vrcpy.currentuser.CurrentUser
    .. automethod:: vrcpy.currentuser.CurrentUser.delete_account() -> vrcpy.currentuser.CurrentUser

World
~~~~~~

.. _vrcpy.limitedworld.LimitedWorld:
.. autoclass:: vrcpy.limitedworld.LimitedWorld
    :members:

.. _vrcpy.world.World:
.. autoclass:: vrcpy.world.World
    :inherited-members:
    :members:

Avatar
~~~~~~~

.. _vrcpy.avatar.Avatar:
.. autoclass:: vrcpy.avatar.Avatar
    :members:

Favorite
~~~~~~~~~

.. _vrcpy.favoritegroup.FavoriteGroup:
.. autoclass:: vrcpy.favoritegroup.FavoriteGroup
    
.. _vrcpy.favoritegroup.FavoriteWorldGroup:
.. autoclass:: vrcpy.favoritegroup.FavoriteWorldGroup

.. _vrcpy.favoritegroup.FavoriteFriendGroup:
.. autoclass:: vrcpy.favoritegroup.FavoriteFriendGroup

.. _vrcpy.favoritegroup.FavoriteAvatarGroup:
.. autoclass:: vrcpy.favoritegroup.FavoriteAvatarGroup

File
~~~~~

.. _vrcpy.file.File:
.. autoclass:: vrcpy.file.File
    :members:

.. _vrcpy.types.file.FileAsset:
.. autoclass:: vrcpy.types.file.FileAsset

.. _vrcpy.types.file.FileVersion:
.. autoclass:: vrcpy.types.file.FileVersion
    :members:

.. _vrcpy.types.file.FileStatus:
.. autoclass:: vrcpy.types.file.FileStatus
    :members:

Moderation
~~~~~~~~~~~

.. _vrcpy.moderation.Moderation:
.. autoclass:: vrcpy.moderation.Moderation
    :members:

Notification
~~~~~~~~~~~~~

.. _vrcpy.notification.Notification
.. autoclass:: vrcpy.notification.Notification
    :members:

Types
~~~~~~

types.enum
------------

.. _vrcpy.types.enum.UserStatus
.. autoenum:: vrcpy.types.enum.UserStatus

.. _vrcpy.types.enum.PlayerModerationType
.. autoenum:: vrcpy.types.enum.PlayerModerationType

.. _vrcpy.types.enum.DeveloperType
.. autoenum:: vrcpy.types.enum.DeveloperType

.. _vrcpy.types.enum.NotificationType
.. autoenum:: vrcpy.types.enum.NotificationType

.. _vrcpy.types.enum.SearchGenericType
.. autoenum:: vrcpy.types.enum.SearchGenericType

Exceptions
~~~~~~~~~~~

errors.RequestErrors
---------------------

.. _vrcpy.errors.RequestErrors.RateLimit:
.. autoexception:: vrcpy.errors.RequestErrors.RateLimit

errors.ClientErrors
--------------------

.. _vrcpy.errors.ClientErrors.MfaRequired:
.. autoexception:: vrcpy.errors.ClientErrors.MfaRequired

.. _vrcpy.errors.ClientErrors.MfaInvalid:
.. autoexception:: vrcpy.errors.ClientErrors.MfaInvalid

.. _vrcpy.errors.ClientErrors.InvalidEventFunction:
.. autoexception:: vrcpy.errors.ClientErrors.InvalidEventFunction

.. _vrcpy.errors.ClientErrors.InvalidAuthToken:
.. autoexception:: vrcpy.errors.ClientErrors.InvalidAuthToken

Utility Helpers
~~~~~~~~~~~~~~~~

.. _vrcpy.util.threadwrap.ThreadWrap:
.. autoclass:: vrcpy.util.threadwrap.ThreadWrap

.. toctree::
   :maxdepth: 2
   :caption: Contents: