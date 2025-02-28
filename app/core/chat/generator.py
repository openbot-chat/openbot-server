import threading
import traceback
import asyncio
from core.callbacks.streaming import ThreadedGenerator, ChainStreamHandler


class ChatGenerator:
    def generator(self, agent_runner, message):
        g = ThreadedGenerator()
        threading.Thread(target=self.llm_thread, args=(agent_runner, g, message)).start()
        return g

    def llm_thread(self, agent_runner, g, message):
        stream_handler = ChainStreamHandler(g)

        try:
          async def wrapper():
            return await agent_runner.run(message, stream_handler=stream_handler)
          asyncio.run(wrapper())
        except Exception as e:
          print(traceback.format_exc())
        finally:
          g.close()