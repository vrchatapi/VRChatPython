.. currentmodule:: vrcpy

API Reference
=============

Client
~~~~~~~

.. autoclass:: vrcpy.Client
    :members:

User
~~~~~

.. _vrcpy.FriendStatus:
.. autoclass:: vrcpy.FriendStatus
    :members:

.. _vrcpy.LimitedUser:
.. autoclass:: vrcpy.LimitedUser
    :members:

.. _vrcpy.User:
.. autoclass:: vrcpy.User
    :inherited-members:
    :members:

.. _vrcpy.CurrentUser:
.. autoclass:: vrcpy.CurrentUser
    :inherited-members:
    :members:

World
~~~~~~

.. _vrcpy.LimitedWorld:
.. autoclass:: vrcpy.LimitedWorld
    :members:

.. _vrcpy.World:
.. autoclass:: vrcpy.World
    :inherited-members:
    :members:

.. _vrcpy.Instance:
.. autoclass:: vrcpy.Instance
    :members:

Avatar
~~~~~~~

.. _vrcpy.Avatar:
.. autoclass:: vrcpy.Avatar
    :members:

Favorite
~~~~~~~~~

.. _vrcpy.WorldFavorite:
.. autoclass:: vrcpy.WorldFavorite
    
.. _vrcpy.AvatarFavorite:
.. autoclass:: vrcpy.AvatarFavorite

.. _vrcpy.FriendFavorite:
.. autoclass:: vrcpy.FriendFavorite

.. _vrcpy.WorldFavoriteGroup:
.. autoclass:: vrcpy.WorldFavoriteGroup

.. _vrcpy.AvatarFavoriteGroup:
.. autoclass:: vrcpy.AvatarFavoriteGroup

.. _vrcpy.FriendFavoriteGroup:
.. autoclass:: vrcpy.FriendFavoriteGroup

File
~~~~~

.. _vrcpy.File:
.. autoclass:: vrcpy.File
    :members:

.. _vrcpy.FileVersion:
.. autoclass:: vrcpy.FileVersion
    :members:

.. _vrcpy.IconFile:
.. autoclass:: vrcpy.IconFile
    :members:

Moderation
~~~~~~~~~~~

.. _vrcpy.PlayerModeration:
.. autoclass:: vrcpy.PlayerModeration
    :members:
    :exclude-members: build_moderation

.. _vrcpy.BlockPlayerModeration:
.. autoclass:: vrcpy.BlockPlayerModeration
    :inherited-members:
    :members:
    :exclude-members: build_moderation, create_moderation

.. _vrcpy.ShowAvatarModeration:
.. autoclass:: vrcpy.ShowAvatarModeration
    :inherited-members:
    :members:
    :exclude-members: build_moderation, create_moderation

.. _vrcpy.HideAvatarModeration:
.. autoclass:: vrcpy.HideAvatarModeration
    :inherited-members:
    :members:
    :exclude-members: build_moderation, create_moderation

.. _vrcpy.MutePlayerModeration:
.. autoclass:: vrcpy.MutePlayerModeration
    :inherited-members:
    :members:
    :exclude-members: build_moderation, create_moderation

.. _vrcpy.UnmutePlayerModeration:
.. autoclass:: vrcpy.UnmutePlayerModeration
    :inherited-members:
    :members:
    :exclude-members: build_moderation, create_moderation

Notification
~~~~~~~~~~~~~

.. _vrcpy.InviteNotification:
.. autoclass:: vrcpy.InviteNotification
    :inherited-members:
    :members:

.. _vrcpy.RequestInviteNotification:
.. autoclass:: vrcpy.RequestInviteNotification
    :inherited-members:
    :members:

.. _vrcpy.RequestInviteResponseNotification:
.. autoclass:: vrcpy.RequestInviteResponseNotification
    :inherited-members:
    :members:

.. _vrcpy.FriendRequestNotification:
.. autoclass:: vrcpy.FriendRequestNotification
    :inherited-members:
    :members:

Exceptions
~~~~~~~~~~~

errors.RequestErrors
---------------------

.. _vrcpy.errors.RequestErrors.NoSession:
.. autoexception:: vrcpy.errors.RequestErrors.NoSession

.. _vrcpy.errors.RequestErrors.SessionExists:
.. autoexception:: vrcpy.errors.RequestErrors.SessionExists

.. _vrcpy.errors.RequestErrors.RequestError:
.. autoexception:: vrcpy.errors.RequestErrors.RequestError

.. _vrcpy.errors.RequestErrors.RateLimit:
.. autoexception:: vrcpy.errors.RequestErrors.RateLimit

.. _vrcpy.errors.RequestErrors.Unauthorized:
.. autoexception:: vrcpy.errors.RequestErrors.Unauthorized

errors.VRChatErrors
--------------------

.. _vrcpy.errors.VRChatErrors.ServiceUnavailable:
.. autoexception:: vrcpy.errors.VRChatErrors.ServiceUnavailable

errors.ClientErrors
--------------------

.. _vrcpy.errors.ClientErrors.OutOfDate:
.. autoexception:: vrcpy.errors.ClientErrors.OutOfDate

.. _vrcpy.errors.ClientErrors.MissingCredentials:
.. autoexception:: vrcpy.errors.ClientErrors.MissingCredentials

.. _vrcpy.errors.ClientErrors.MfaRequired:
.. autoexception:: vrcpy.errors.ClientErrors.MfaRequired

.. _vrcpy.errors.ClientErrors.MfaInvalid:
.. autoexception:: vrcpy.errors.ClientErrors.MfaInvalid

.. _vrcpy.errors.ClientErrors.InvalidEventFunction:
.. autoexception:: vrcpy.errors.ClientErrors.InvalidEventFunction

.. _vrcpy.errors.ClientErrors.InvalidAuthToken:
.. autoexception:: vrcpy.errors.ClientErrors.InvalidAuthToken

errors.ObjectErrors
--------------------

.. _vrcpy.errors.ObjectErrors.IntegretyError:
.. autoexception:: vrcpy.errors.ObjectErrors.IntegretyError

.. _vrcpy.errors.ObjectErrors.NotFriends:
.. autoexception:: vrcpy.errors.ObjectErrors.NotFriends

.. _vrcpy.errors.ObjectErrors.AlreadyFriends:
.. autoexception:: vrcpy.errors.ObjectErrors.AlreadyFriends

.. _vrcpy.errors.ObjectErrors.InvalidGroupName:
.. autoexception:: vrcpy.errors.ObjectErrors.InvalidGroupName

.. _vrcpy.errors.ObjectErrors.NotOwned:
.. autoexception:: vrcpy.errors.ObjectErrors.NotOwned

Utility Helpers
~~~~~~~~~~~~~~~~

.. _vrcpy.util.auto_page_coro:
.. automethod:: vrcpy.util.auto_page_coro

.. _vrcpy.util.TaskWrapReturn:
.. autoclass:: vrcpy.util.TaskWrapReturn

.. _vrcpy.util.find_in_list_via_attribute:
.. automethod:: vrcpy.util.find_in_list_via_attribute

.. toctree::
   :maxdepth: 2
   :caption: Contents: