"""WebSocket manager for real-time task progress updates."""

from typing import Dict, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for task progress updates."""

    def __init__(self):
        # Map of task_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """
        Accept a new WebSocket connection and subscribe to task updates.

        Args:
            websocket: The WebSocket connection
            task_id: The task ID to subscribe to
        """
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()

        self.active_connections[task_id].add(websocket)
        logger.info(f"Client connected to task {task_id}. Total connections: {len(self.active_connections[task_id])}")

    def disconnect(self, websocket: WebSocket, task_id: str):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection
            task_id: The task ID
        """
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)

            # Clean up empty task sets
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

            logger.info(f"Client disconnected from task {task_id}")

    async def send_message(self, task_id: str, message: dict):
        """
        Send a message to all connections subscribed to a task.

        Args:
            task_id: The task ID
            message: The message dictionary to send (will be JSON encoded)
        """
        if task_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, task_id)

    def get_connection_count(self, task_id: str) -> int:
        """
        Get the number of active connections for a task.

        Args:
            task_id: The task ID

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(task_id, set()))


# Global connection manager instance
manager = ConnectionManager()
