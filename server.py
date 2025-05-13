import socket
import uvicorn
from fastapi import FastAPI


class Server:
    app: FastAPI
    server: uvicorn.Server
    url: str

    def __init__(self, port):
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_socket.connect(("8.8.8.8", 80))
        ip = local_socket.getsockname()[0]
        local_socket.close()

        self.url = f"http://{ip}:{port}"
        self.app = FastAPI()

        self.server = uvicorn.Server(
            uvicorn.Config(self.app, host="0.0.0.0", port=port)
        )

    def run_server(self):
        self.server.run()
