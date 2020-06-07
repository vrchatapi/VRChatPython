from typing import Optional, List, Union
from vrcpy import objects, aobjects

oString = Optional[str]
oBoolean = Optional[bool]
oInteger = Optional[int]

AvatarList = Union[List[objects.Avatar], List[aobjects.Avatar]]
UserList = Union[List[objects.User], List[objects.LimitedUser], List[aobjects.User],\
    List[aobjects.LimitedUser]]

Avatar = Union[objects.Avatar, aobjects.Avatar]
User = Union[objects.User, objects.LimitedUser, aobjects.User, aobjects.LimitedUser]
CurrentUser = Union[objects.CurrentUser, aobjects.CurrentUser]
