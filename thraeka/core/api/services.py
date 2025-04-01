import json
from datetime import date, datetime
from typing import Any

import pymupdf
from config.settings import OPENAI_API_KEY
from core.models import Txn
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Sum
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


class SummaryCache:
    """
    Manage caching of txn summaries over date range

    Method:
        Public:
            - get txn summary for date range
            - update txn summaries with input txn
        Private:
            - generate summary cache key
            - save data to cache
            - save summary cache key to cache key set
            - calculate summary from database

    Attribute:
        SUMMARY_CACHE_KEY_LIST (str): Cache key for set of summary cache keys

    To Do:
        - clean up cache key list if associated cache does not exist
        - current update does not take in old data, therefore two cache access to update: remove
        old txn details and add new txn details. Improve so only 1 cache access is required
        - error checking
        - add locks

    """

    SUMMARY_CACHE_KEY_LIST = "filter"

    def _gen_summary_cache_key(self, start_date: date, end_date: date) -> str:
        """Generate txn summary cache key"""
        return f"summary:{start_date}_to_{end_date}"

    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        """Save to data to cache"""
        cache.set(cache_key, data, timeout=1800)

    def _save_summary_cache_key(self, cache_key: str) -> None:
        """Add txn summary cache key to cache key set"""
        summary_cache_keys = cache.get(self.SUMMARY_CACHE_KEY_LIST) or set()
        summary_cache_keys.add(cache_key)
        cache.set(self.SUMMARY_CACHE_KEY_LIST, summary_cache_keys, timeout=1800)

    def _calc_summary(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Calculate the txn summary within date range from database"""
        txns = Txn.objects.filter(date__gte=start_date, date__lte=end_date)

        total = round(txns.aggregate(total=Sum("amount"))["total"], 2)
        total_by_cat = txns.values("category").annotate(total=Sum("amount"))
        category_totals = {
            item["category"]: round(item["total"], 2) for item in total_by_cat
        }

        return {
            "date_range": [start_date, end_date],
            "total": total,
            "total_by_cat": category_totals,
        }

    def get(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Get cached txn summary or calculate if not available"""
        cache_key = self._gen_summary_cache_key(start_date, end_date)
        summary = cache.get(cache_key)

        if summary is None:
            summary = self._calc_summary(start_date, end_date)
            self._save_to_cache(cache_key, summary)
            self._save_summary_cache_key(cache_key)
        return summary

    def update(self, txn_date: date, amount: float, category_name: str) -> None:
        """Update all cached txn summary"""
        # Get set all cached txn summary keys
        summary_cache_keys = cache.get(self.SUMMARY_CACHE_KEY_LIST)
        if summary_cache_keys is None:
            return
        for summary_cache_key in summary_cache_keys:
            # Summary cache key contains start and end date
            start_date = datetime.strptime(summary_cache_key[8:18], "%Y-%m-%d").date()
            end_date = datetime.strptime(summary_cache_key[22:32], "%Y-%m-%d").date()
            # If txn date is within current txn summary range, update
            if not (start_date <= txn_date <= end_date):
                continue
            summary = cache.get(summary_cache_key)
            if summary:
                summary["total"] += amount
                if category_name in summary["total_by_cat"]:
                    summary["total_by_cat"][category_name] += amount
                else:
                    summary["total_by_cat"][category_name] = amount
                if summary["total_by_cat"][category_name] <= 0:
                    summary["total_by_cat"].pop(category_name)
                self._save_to_cache(summary_cache_key, summary)
