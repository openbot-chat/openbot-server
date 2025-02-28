from channels.connection_handler import ConnectionHandler
from channels.connection import Connection
from typing import Dict

class HubManager(ConnectionHandler):
  def __init__(self):
    self.connections = {}
  
  def on_connect(self, connection: Connection):
    self.connections[connection.id] = connection
    print('hub on_connect', len(self.connections))

  def on_disconnect(self, connection: Connection):
    del self.connections[connection.id]
    print('hub on_disconnect', len(self.connections))

  def on_message(self, msg: Dict, connection: Connection):
    pass

  def on_error(self, err: Exception, connection: Connection):
    pass
  
  def get(self, id: str) -> Connection:
    return self.connections[id]