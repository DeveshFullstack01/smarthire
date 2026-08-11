import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time user notifications.
    """

    async def connect(self):
        """
        Connect authenticated users to their personal notification group.
        """

        user = self.scope["user"]

        if user.is_anonymous:
            logger.warning("Anonymous WebSocket connection rejected.")
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        logger.info(
            "WebSocket connected. user_id=%s",
            user.id,
        )

    async def disconnect(self, close_code):
        """
        Remove the user from the notification group.
        """

        user = self.scope["user"]

        if not user.is_anonymous:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

            logger.info(
                "WebSocket disconnected. user_id=%s",
                user.id,
            )

    async def receive(self, text_data):
        """
        Currently the browser does not send messages.
        Reserved for future chat features.
        """
        pass

    async def send_notification(self, event):
        """
        Receive a notification from the channel layer and
        send it to the browser.
        """

        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "url": event["url"],
                    "created_at": event["created_at"],
                }
            )
        )