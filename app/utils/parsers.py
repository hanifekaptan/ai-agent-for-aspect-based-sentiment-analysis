"""

"""

from typing import Any, Dict, List, Optional
import pandas as pd
import logging

from app.utils.sanitizer import sanitize_comment
from app.utils.language_detector import detect_lang

log = logging.getLogger(__name__)

def create_df(uploaded_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a standardized DataFrame from uploaded CSV data.

    Args:
        uploaded_df (pd.DataFrame): The DataFrame loaded from the uploaded CSV file.

    Returns:
        pd.DataFrame: A standardized DataFrame with 'id', 'comments', and 'language' columns.
    """
    df = pd.DataFrame()

    if len(uploaded_df.columns) == 1:
        df['id'] = [str(i + 1) for i in range(len(uploaded_df))]
        df['comments'] = uploaded_df.iloc[:, 0].astype(str)

    elif uploaded_df.columns.str.lower().str.strip().isin(["comments", "id"]).all():
        df[["id", "comments"]] = uploaded_df[["id", "comments"]].astype(str)
    
    else:
        raise ValueError("CSV must contain comments data.")

    df["comments"] = df["comments"].apply(sanitize_comment)
    df["language"] = df["comments"].apply(detect_lang)

    return df.to_dict(orient='records')


def parse_data(inputs: Any) -> List[Dict[str, str]]:
    """
    Parses input data, which can be a string, a file-like object, or a path to a CSV file.

    Args:
        inputs (Any): The input data, which can be a string, a file-like object, or a path to a CSV file.

    Returns:
        List[Dict[str, str]]: The parsed data as a list of dictionaries.
    """
    def looks_like_file(obj) -> bool:
        if hasattr(obj, "read") and callable(getattr(obj, "read")):
            return True
        if getattr(obj, "filename", None) or getattr(obj, "name", None):
            return True
        return False

    if isinstance(inputs, str):
        df = pd.DataFrame(columns=["id", "comments"], data=[["1", inputs]])
        return create_df(df)
    elif looks_like_file(inputs):
        file_obj = getattr(inputs, 'file', inputs)
        try:
            file_obj.seek(0)
        except Exception:
            pass

        import io
        if isinstance(file_obj, (bytes, bytearray)):
            file_obj = io.BytesIO(file_obj)

        uploaded_df = pd.read_csv(file_obj)
        return create_df(uploaded_df)

def batch_packing(items: List[Dict], max_items: int = 10) -> List[List[Dict]]:
    """
    Öğeleri `max_items` kullanarak sabit boyutlu gruplara ayırır.
    """
    batches: List[List[Dict]] = []
    if not items:
        return batches

    for i in range(0, len(items), max_items):
        batches.append(items[i:i + max_items])

    log.info('Packed %d items into %d batches (max items %d)', len(items), len(batches), max_items)
    return batches

def toon_to_dicts(llm_output: str) ->  List[Dict[str, Any]]:
    """
    Parses TOON-formatted LLM output into a list of dictionaries.

    Args:
        llm_output (str): The raw LLM output string in TOON format.

    Returns:
        List[Dict[str, Any]]: A list of parsed dictionaries.
    """
    results: List[Dict[str, Any]] = []
    if not llm_output:
        return results

    for line in llm_output.strip().splitlines():
        line = line.strip()
        if not line or not line.startswith('L:'):
            continue
        rest = line[2:]
        if '|' not in rest:
            continue
        id_part, aspects_part = rest.split('|', 1)
        id_part = id_part.strip()

        aspects_list: List[Dict[str, str]] = []
        for a in aspects_part.split(';;'):
            a = a.strip()
            if not a:
                continue
            parts = [p.strip() for p in a.split('~')]
            if len(parts) >= 2:
                term = parts[0]
                sentiment = parts[1]
                aspects_list.append({'term': term, 'sentiment': sentiment})

        results.append({'id': id_part, 'aspects': aspects_list})

    return results