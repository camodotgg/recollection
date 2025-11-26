#!/usr/bin/env python3
"""Test WebSocket connection for real-time task progress updates."""

import asyncio
import websockets
import json
import sys


async def test_websocket(task_id: str):
    """
    Connect to WebSocket and receive real-time task progress updates.

    Args:
        task_id: The task ID to monitor
    """
    uri = f"ws://localhost:8000/ws/tasks/{task_id}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Waiting for messages...\n")

            # Receive messages
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    event = data.get("event")
                    print(f"[{event}]", json.dumps(data, indent=2))

                    # Exit on completion or failure
                    if event in ["completed", "failed"]:
                        print("\nTask finished!")
                        break

                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed by server")
                    break

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_websocket.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    asyncio.run(test_websocket(task_id))
