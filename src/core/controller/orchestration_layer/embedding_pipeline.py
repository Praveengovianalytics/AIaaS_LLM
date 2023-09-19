from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import sys
from core.settings import Param


sys.path.append("..")

embedding_model = HuggingFaceEmbeddings(
    model_name=Param.EMBEDDING_MODEL_PATH,
    model_kwargs={"device": Param.EMBEDDING_DEVICE},
)


class EmbeddingPipeline:
    """
    class to generate Embedding using FAISS
    """

    def __init__(self, tmp_file_path, user):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class with all of its attributes and methods.
        The __init__ function takes in a tmp_file_path, which it uses to load data from a csv file into an attribute called self.data,
        which is then used to create an attribute called self.db that contains all of our documents.

        Args:
            self: Represent the instance of the class
            tmp_file_path: Store the path of the temporary file
            user: Create a new location for each user

        Returns:
            Nothing
        """
        self.tmp_file_path = tmp_file_path
        self.data = self.load_data_from_csv()
        self.user = user
        self.db = self.create_db_from_documents()

    def load_data_from_csv(self):
        """
        The load_data_from_csv function loads data from a CSV file.

        Args:
            self: Represent the instance of the class

        Returns:
            A dataframe object

        Doc Author:
            Trelent
        """
        loader = CSVLoader(
            file_path=self.tmp_file_path,
            encoding=Param.CSV_ENCODING,
            csv_args={"delimiter": Param.CSV_DELIMITER},
        )
        return loader.load()

    def create_db_from_documents(self):
        """
        The create_db_from_documents function takes the data from the documents and creates a database using FAISS.
            The function returns a database that can be used to search for similar documents.

        Args:
            self: Represent the instance of the class

        Returns:
            A faiss database

        """
        return FAISS.from_documents(self.data, embedding_model)

    def save_db_local(self):
        """
        The save_db_local function saves the database to a local file.

        Args:
            self: Represent the instance of the class

        Returns:
            The database object

        """
        self.db.save_local(Param.EMBEDDING_SAVE_PATH + self.user + "/", "index")

    def get_db(self):
        """
        The get_db function return the db


        Args:
            self: Represent the instance of the class

        """
        return self.db


def load_embedding(filepath):
    """
    The load_embedding function loads a pre-trained embedding model from the specified filepath.

    Args:
        filepath: Specify the location of the file to be loaded

    Returns:
        An index object"""
    return FAISS.load_local(filepath, embedding_model, "index")
