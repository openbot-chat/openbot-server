from langchain.document_loaders import WebBaseLoader


loader = WebBaseLoader("https://www.baidu.com/")

data = loader.load()

print(data)