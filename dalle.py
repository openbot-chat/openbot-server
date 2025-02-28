
import openai
from app.config import *

client = openai.OpenAI()

prompt = "画一只松鼠"

response = client.images.generate(prompt=prompt, n=1, size="1024x1024", model="dall-e-3")

print('response: ', response.data)