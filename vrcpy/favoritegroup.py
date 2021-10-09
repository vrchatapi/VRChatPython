from .model import Model

class FavoriteGroup(Model):
    @staticmethod
    def favorite_group(self, loop, data):
        groups = {
            "world": FavoriteWorldGroup,
            "friend": FavoriteFriendGroup,
            "avatar": FavoriteAvatarGroup
        }

        return groups[data["type"]](loop, data)

    def __init__(self, loop, data):
        super().__init__(loop, data)

class FavoriteWorldGroup(FavoriteGroup):
    pass

class FavoriteFriendGroup(FavoriteGroup):
    pass

class FavoriteAvatarGroup(FavoriteGroup):
    pass