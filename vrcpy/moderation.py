from .types.enum import PlayerModerationType
from .decorators import auth_required
from .model import Model

import logging
import time

class Moderation(Model):
    __slots__ = (
        "created", "id", "source_display_name", "source_user_id",
        "target_display_name", "target_user_id", "type"
    )

    __types__ = {
        "created": time.struct_time,
        "id": str,
        "source_display_name": str,
        "source_user_id": str,
        "target_display_name": str,
        "target_user_id": str,
        "type": PlayerModerationType
    }

    @auth_required
    async def delete_moderation(self):
        logging.debug("Deleting moderation %s" % self.id)

        await self.client.request.delete("/auth/user/playermoderations/%s" % self.id)