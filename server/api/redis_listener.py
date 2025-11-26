"""Redis pub/sub listener for task progress events."""

import asyncio
import json
import logging
import os
import redis.asyncio as aioredis
from server.api.websocket import manager

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisListener:
    """Listens to Redis pub/sub and forwards messages to WebSocket clients."""

    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.listener_task = None
        self.running = False

    async def start(self):
        """Start the Redis pub/sub listener."""
        if self.running:
            logger.warning("Redis listener already running")
            return

        try:
            self.redis_client = await aioredis.from_url(REDIS_URL)
            self.pubsub = self.redis_client.pubsub()

            # Subscribe to all task channels using pattern matching
            await self.pubsub.psubscribe("task:*")

            self.running = True
            self.listener_task = asyncio.create_task(self._listen())
            logger.info("Redis pub/sub listener started")

        except Exception as e:
            logger.error(f"Failed to start Redis listener: {e}")
            raise

    async def stop(self):
        """Stop the Redis pub/sub listener."""
        if not self.running:
            return

        self.running = False

        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

        logger.info("Redis pub/sub listener stopped")

    async def _listen(self):
        """Listen for Redis pub/sub messages and forward to WebSocket clients."""
        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break

                if message["type"] == "pmessage":
                    channel = message["channel"].decode("utf-8")
                    data = message["data"].decode("utf-8")

                    # Extract task_id from channel name (format: "task:task_id")
                    task_id = channel.split(":", 1)[1]

                    try:
                        payload = json.loads(data)
                        await manager.send_message(task_id, payload)
                        logger.debug(f"Forwarded message to task {task_id}: {payload.get('event')}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode Redis message: {e}")
                    except Exception as e:
                        logger.error(f"Error forwarding message: {e}")

        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
            if self.running:
                # Try to restart after a delay
                await asyncio.sleep(5)
                if self.running:
                    logger.info("Attempting to restart Redis listener")
                    await self.start()


# Global listener instance
redis_listener = RedisListener()
