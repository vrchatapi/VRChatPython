from .types.enum import PlayerModerationType
from .decorators import auth_required
from .model import Model
from .types.rdict import RDict

import logging
import time

class Moderation(Model):
    __slots__ = (
        "created", "id", "source_display_name", "source_user_id",
        "target_display_name", "target_user_id", "type"
    )

    __types__ = RDict({
        "created": time.struct_time,
        "id": str,
        "source_display_name": str,
        "source_user_id": str,
        "target_display_name": str,
        "target_user_id": str,
        "type": PlayerModerationType
    })

    async def delete(self):
        """Deletes this moderation"""
        await self.client.delete_moderation(self.id)