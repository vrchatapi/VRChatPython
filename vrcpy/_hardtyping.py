from typing import Optional, List, Union
from vrcpy import objects, aobjects

oString = Optional[str]
oBoolean = Optional[bool]
oInteger = Optional[int]

AvatarList = Union[List[objects.Avatar], List[aobjects.Avatar]]
