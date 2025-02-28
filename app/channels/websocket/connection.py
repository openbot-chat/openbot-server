from fastapi import WebSocket, WebSocketDisconnect
import logging
from channels.connection_handler import ConnectionHandler 
from channels.connection import Connection
from nanoid import generate
from typing import Any
import traceback
import time

class WebSocketConnection(Connection):
  def __init__(self, websocket: WebSocket, connection_handler: ConnectionHandler):
    self.id = generate()
    self.websocket = websocket
    self.connection_handler = connection_handler

  async def serve(self):
    await self.websocket.accept()

    self.connection_handler.on_connect(self)
    while True:
      try:
        message = await self.websocket.receive_json()
        await self.connection_handler.on_message(message, self)
      except WebSocketDisconnect:
        logging.info("websocket disconnect")
        self.connection_handler.on_disconnect(self)

        break
      except Exception as e:
        print('websocket err: ', traceback.format_exc())
        self.connection_handler.on_error(e, self)
    
  async def send(self, msg: Any):
    await self.websocket.send_json(msg)