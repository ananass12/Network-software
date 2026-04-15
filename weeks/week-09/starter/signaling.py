import asyncio
import websockets
import json
import os

# Простой Signaling сервер для WebRTC
# Он должен пересылать сообщения от одного клиента всем остальным (или конкретному собеседнику)

CONNECTIONS = set()

async def handler(websocket):
    CONNECTIONS.add(websocket)
    print(f"Новое подключение. Всего клиентов: {len(CONNECTIONS)}")
    try:
        async for message in websocket:          
            # Парсим JSON, чтобы убедиться, что это валидное сообщение
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            # Отправляем всем, кроме отправителя
            for conn in list(CONNECTIONS):
                if conn is websocket:
                    continue
                try:
                    await conn.send(message)
                except websockets.exceptions.ConnectionClosed:
                    pass
    finally:
        CONNECTIONS.remove(websocket)
        print(f"Клиент отключился. Всего клиентов: {len(CONNECTIONS)}")

async def main():
    host = os.environ.get("SIGNALING_HOST", "0.0.0.0")
    port = int(os.environ.get("SIGNALING_PORT", "8765"))
    async with websockets.serve(handler, host, port):
        print(f"Signaling server: ws://127.0.0.1:{port} (listen {host}:{port})")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
