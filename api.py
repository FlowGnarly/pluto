import asyncio
import io
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketState
from globals import server
from fastapi import WebSocket, WebSocketDisconnect
import WinTmp
import psutil


class ConnectionManager:
    clients: list[WebSocket]
    pending: dict[str, any]

    def __init__(self):
        self.pending = dict()
        self.clients = []

    async def connect(self, client: WebSocket):
        await client.accept()
        self.clients.append(client)

        await self.update_client(client=client)

    def disconnect(self, client: WebSocket):
        self.clients.remove(client)

    def add_pending_message(self, channel: str, json: any):
        self.pending[channel] = json

    async def update_client(self, client: WebSocket):
        if client.application_state == WebSocketState.CONNECTED:
            await client.send_json(self.pending)
        else:
            self.disconnect(client)

    async def send_pending_messages(self):
        for client in self.clients:
            await self.update_client(client=client)


system_information = ConnectionManager()


async def system_information_main():
    while True:
        if len(system_information.clients) == 0:
            await asyncio.sleep(0.25)
            continue

        system_information.pending.clear()

        memory = psutil.virtual_memory()

        system_information.add_pending_message(
            "memory_usage",
            {
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_free": memory.free,
                "memory_total": memory.total,
            },
        )

        system_information.add_pending_message(
            "cpu_usage", {"cpu_percent": psutil.cpu_percent()}
        )

        system_information.add_pending_message(
            "gpu_usage", {"gpu_temps": WinTmp.GPU_Temps()}
        )

        await system_information.send_pending_messages()

        await asyncio.sleep(5)


@server.app.on_event("startup")
def startup_event():
    asyncio.create_task(system_information_main())


@server.app.get("/")
async def get():
    html_file = io.open("prototype_page.html", "r")
    html = html_file.read()
    html_file.close()

    return HTMLResponse(html)


@server.app.websocket("/system_information")
async def websocket_read_root(websocket: WebSocket):
    await system_information.connect(websocket)

    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except Exception as e:
        print(f"Client disconnected unexpectedly: {e}")
    finally:
        system_information.disconnect(websocket)
