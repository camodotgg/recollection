"""WebSocket routes for real-time task progress updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from server.db.database import get_db
from server.db.models import TaskStatusDB
from server.api.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def task_progress_websocket(
    websocket: WebSocket,
    task_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time task progress updates.

    Clients connect to this endpoint to receive real-time progress updates
    for a specific task. The connection will receive:
    - Initial task status on connection
    - Real-time progress updates as the task executes
    - Completion or failure notifications

    Args:
        websocket: WebSocket connection
        task_id: The task ID to subscribe to
        session: Database session

    Message format:
        {
            "event": "progress" | "completed" | "failed" | "status",
            "task_id": "uuid",
            "percent": 0-100,  # for progress events
            "step": "description",  # for progress events
            "result": {...},  # for completed events
            "error": "message"  # for failed events
        }
    """
    await manager.connect(websocket, task_id)

    try:
        # Send initial task status
        result = await session.execute(
            select(TaskStatusDB).where(TaskStatusDB.task_id == task_id)
        )
        task_status = result.scalar_one_or_none()

        if task_status:
            initial_message = {
                "event": "status",
                "task_id": task_id,
                "status": task_status.status,
                "progress_percent": task_status.progress_percent,
                "current_step": task_status.current_step,
                "result": task_status.result_json,
                "error": task_status.error_message,
                "created_at": task_status.created_at.isoformat() if task_status.created_at else None,
                "started_at": task_status.started_at.isoformat() if task_status.started_at else None,
                "completed_at": task_status.completed_at.isoformat() if task_status.completed_at else None,
            }
            await websocket.send_json(initial_message)
            logger.info(f"Sent initial status for task {task_id}: {task_status.status}")
        else:
            # Task not found
            await websocket.send_json({
                "event": "error",
                "task_id": task_id,
                "error": "Task not found"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Keep connection alive and wait for client disconnect
        # Real-time updates are sent via Redis pub/sub listener
        while True:
            # Receive messages from client (mostly for keepalive)
            data = await websocket.receive_text()
            # Echo back to confirm connection is alive
            if data == "ping":
                await websocket.send_json({"event": "pong"})

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection for task {task_id}: {e}")
    finally:
        manager.disconnect(websocket, task_id)
