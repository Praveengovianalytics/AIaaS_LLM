from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import sys


sys.path.append("..")
from core.settings import Param

embedding_model=HuggingFaceEmbeddings(
            model_name=Param.EMBEDDING_MODEL_PATH,
            model_kwargs={'device': Param.EMBEDDING_DEVICE}
        )
class EmbeddingPipeline:

    def __init__(self, tmp_file_path,user):
        self.tmp_file_path = tmp_file_path
        self.data = self.load_data_from_csv()
        self.user=user
        self.db = self.create_db_from_documents()

    def load_data_from_csv(self):
        loader = CSVLoader(file_path=self.tmp_file_path, encoding=Param.CSV_ENCODING, csv_args={
            'delimiter': Param.CSV_DELIMITER
        })
        return loader.load()

    def create_db_from_documents(self):
        return FAISS.from_documents(self.data, embedding_model)

    def save_db_local(self):
        self.db.save_local(Param.EMBEDDING_SAVE_PATH+self.user+"/",'index')

    def get_db(self):

        return self.db

def load_embedding(filepath):
    return    FAISS.load_local(filepath,embedding_model,'index')
