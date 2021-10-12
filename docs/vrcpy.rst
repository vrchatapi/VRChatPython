.. currentmodule:: vrcpy

API Reference
=============

Client
~~~~~~~

.. autoclass:: vrcpy.Client
    :members:
    :exclude-members: on_connect, on_ready, on_disconnect, on_friend_online, on_friend_offline, on_friend_active, on_friend_add, on_friend_delete, on_friend_update, on_friend_location, on_notification_received, on_notification_seen, on_notification_response, event
    
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
    :members:

.. _vrcpy.user.User:
.. autoclass:: vrcpy.user.User
    :show-inheritance:
    :members:
    :inherited-members:

.. _vrcpy.currentuser.CurrentUser:
.. autoclass:: vrcpy.currentuser.CurrentUser
    :show-inheritance:
    :members:

World
~~~~~~

.. _vrcpy.limitedworld.LimitedWorld:
.. autoclass:: vrcpy.limitedworld.LimitedWorld
    :members:

.. _vrcpy.world.World:
.. autoclass:: vrcpy.world.World
    :inherited-members:
    :members:

.. _vrcpy.types.instance.Instance:
.. autoclass:: vrcpy.types.instance.Instance
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

Permission
~~~~~~~~~~~

.. _vrcpy.permission.Permission:
.. autoclass:: vrcpy.permission.Permission
    :members:

Moderation
~~~~~~~~~~~

.. _vrcpy.moderation.Moderation:
.. autoclass:: vrcpy.moderation.Moderation
    :members:

Notification
~~~~~~~~~~~~~

.. _vrcpy.notification.Notification:
.. autoclass:: vrcpy.notification.Notification
    :members:

Base Object
~~~~~~~~~~~~

.. _vrcpy.model.Model:
.. autoclass:: vrcpy.model.Model

Types
~~~~~~

types.enum
------------

.. _vrcpy.types.enum.UserStatus:
.. autoenum:: vrcpy.types.enum.UserStatus

.. _vrcpy.types.enum.PlayerModerationType:
.. autoenum:: vrcpy.types.enum.PlayerModerationType

.. _vrcpy.types.enum.DeveloperType:
.. autoenum:: vrcpy.types.enum.DeveloperType

.. _vrcpy.types.enum.NotificationType:
.. autoenum:: vrcpy.types.enum.NotificationType

.. _vrcpy.types.enum.SearchGenericType:
.. autoenum:: vrcpy.types.enum.SearchGenericType

.. _vrcpy.types.enum.ReleaseStatus:
.. autoenum:: vrcpy.types.enum.ReleaseStatus

.. _vrcpy.types.enum.Sort:
.. autoenum:: vrcpy.types.enum.Sort

.. _vrcpy.types.enum.SortOrder:
.. autoenum:: vrcpy.types.enum.SortOrder

.. _vrcpy.types.enum.UserFilter:
.. autoenum:: vrcpy.types.enum.UserFilter

.. _vrcpy.types.enum.FavoriteType:
.. autoenum:: vrcpy.types.enum.FavoriteType

.. _vrcpy.types.enum.Visibility:
.. autoenum:: vrcpy.types.enum.Visibility

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