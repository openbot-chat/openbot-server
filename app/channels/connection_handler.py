from typing import Dict
from fastapi import WebSocket
from channels.connection import Connection

class ConnectionHandler:
  def on_connect(self, connection: Connection):
    pass

  def on_disconnect(self, connection: Connection):
    pass

  def on_message(self, msg: Dict, connection: Connection):
    pass

  def on_error(self, err: Exception, connection: Connection):
    pass