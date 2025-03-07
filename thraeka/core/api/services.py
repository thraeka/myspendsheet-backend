import json

import pymupdf
from config.settings import OPENAI_API_KEY
from core.models import Txn
from django.core.files.uploadedfile import InMemoryUploadedFile
from openai import OpenAI


class OpenAIParser:
    """
    Parser that uses OpenAI to convert bank statement transactions into json
    """

    def __init__(self):
        """
        Initialize OpenAIParser
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.role = "user"

    @property
    def prompt(self) -> str:
        """
        Returns ai prompt used to extract json from bank statement
        """
        return (
            "The file attached is a bank statement converted from pdf to "
            "text via pymupdf. Create a json file with transaction data "
            "from this bank statement. Only output the json contents."
            "Don't even label it as a json. The fields for the"
            f"transactions are {self.fields}. Date should be insame format"
            "as datetime strftime('%Y-%m-%d'). Categories for the "
            f"transactions are {self.categories}."
        )

    @property
    def categories(self) -> str:
        """
        Return transaction categories
        """
        # Currently static, but plan to link to model in future hence @property
        return (
            "Income, Bills, Entertainment, Home, Hobbies, Transportation, "
            "Rent, Car, Groceries, Restuarants, Pet, Utilities, Clothing, "
            "Health, Household Items, Personal, Debt, Education, Work, "
            "Retirement, Investments, Savings, Gifts"
        )

    @property
    def fields(self) -> str:
        """
        Return fields of transaction
        """
        field_list = [field.name for field in Txn._meta.fields]
        field_list.remove("id")
        field_str = ", ".join(field_list)
        return field_str

    def parse_txn_txt_to_json(self, txn_text: str) -> str:
        """
        Input bank statement str and returns str in json format
        """
        # This can take 30 seconds to run. Future run async
        # Need to add token length check
        ai_response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": self.role, "content": self.prompt + "\n" + txn_text}],
        )
        return ai_response.choices[0].message.content


class TxnPdfParser:
    def __init__(self):
        """
        Initalize Transaction PDF Parser
        """
        self.ai_parser = OpenAIParser()

    def _pdf_to_txt(self, pdf: InMemoryUploadedFile) -> str:
        """
        Input file is converted and output as str
        """
        pdf_stream = pdf.read()
        pdf_doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
        pdf_text = ""
        for page in pdf_doc:
            pdf_text = f"{pdf_text} {page.get_text()}"
        return pdf_text

    def txn_file_to_dict(self, pdf: InMemoryUploadedFile) -> list[dict]:
        """
        Input pdf file from request and return list[dict] of txn
        """
        pdf_text = self._pdf_to_txt(pdf)
        txn_json_fmt = self.ai_parser.parse_txn_txt_to_json(pdf_text)
        return json.loads(txn_json_fmt)


class TxnFileParser:
    def __init__(self):
        """
        Initalize Transaction File Parser
        """
        # For now only do pdf file type, but add more in future
        self.pdf_parser = TxnPdfParser()

    def txn_file_to_dict(self, txn_file: InMemoryUploadedFile) -> list[dict]:
        """
        Parse a txn pdf file into list[dict]
        """
        return self.pdf_parser.txn_file_to_dict(txn_file)
