from typing import Dict
from channels.connection import Connection
from channels.connection_handler import ConnectionHandler
from channels.manager.hub_manager import HubManager

class APIHandler(ConnectionHandler):
  def __init__(self, hub_manager: HubManager):
    self.hub_manager = hub_manager

  def on_connect(self, connection: Connection):
    self.hub_manager.on_connect(connection)

  def on_disconnect(self, connection: Connection):
    self.hub_manager.on_disconnect(connection)

  def on_message(self, msg: Dict, connection: Connection):
    pass

  def on_error(self, err: Exception, connection: Connection):
    pass
  