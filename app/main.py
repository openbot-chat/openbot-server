import uvicorn
# import nest_asyncio
# nest_asyncio.apply()

# import nest_asyncio
# nest_asyncio.apply()
import logging

from config import LOG_LEVEL
logging.basicConfig(level=LOG_LEVEL)


if __name__== "__main__":
    uvicorn.run('app:app', host="0.0.0.0", port=5005, reload=True, log_level="info")