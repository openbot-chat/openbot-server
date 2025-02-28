from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.document_loaders import TextLoader
from langchain.document_loaders.image import UnstructuredImageLoader

#import pinecone
from app.config import config

# initialize pinecone
#pinecone.init(
#  api_key="",  # find at app.pinecone.io
#  environment=""  # next to api key in console
#)
import pinecone 
from langchain.document_loaders import TextLoader

pinecone_env = config.get('PINECONE_ENVIRONMENT')
pinecone_api_key = config.get('PINECONE_API_KEY')

pinecone.init(
  api_key=pinecone_api_key,  # find at app.pinecone.io
  environment=pinecone_env  # next to api key in console
)


# loader = TextLoader('./samples/state_of_the_union.txt')
loader = UnstructuredImageLoader(file_path="./dun7.png")
documents = loader.load()
print('documents: ', documents)
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


#vector_db = Pinecone.from_documents(
#    docs,
#    embeddings,
#    index_name = "demo1",
    # connection_args={"api_key": PINECONE_API_KEY, "environment": PINECONE_ENVIROMENT},
#)

vector_db = Pinecone.from_existing_index(
  "demo1",
  embeddings,
)


docs = vector_db.similarity_search("老胡是谁")
print(docs)