import logging
from typing import List, Any
from pathlib import Path
import yaml
from jinja2 import Template


log = logging.getLogger(__name__)


def load_prompt(yaml_path: str):
    """
    Loads a prompt template from a YAML file.

    Args:
        yaml_path (str): The path to the YAML file.

    Returns:
        dict: The parsed YAML content.
    """
    p = Path(yaml_path)
    if not p.exists():
        log.debug('Cannot find prompt at %s, trying prompts dir', yaml_path)
    
    with open(p, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        log.debug('Loaded prompt from %s', p)
        return data


def render(path: str, items: List[str]) -> str:
    """
    Renders a prompt template with the given items and context.

    Args:
        path (str): Can be a full YAML path or a short prompt name like 'absa_v1'.
        items (List[str]): The items to be injected into the template.

    Returns:
        str: The rendered prompt text.
    
    Raises:
        ValueError: If the prompt template is missing.
    """
    prompt_doc = load_prompt(path)
    template_text = prompt_doc.get("template")
    if not template_text:
        raise ValueError(f"Prompt template missing in {path}")
    temp = Template(template_text)
    log.debug('Rendering prompt %s items=%d', path, len(items))
    rendered = temp.render(items=items)
    log.debug('Rendered prompt length=%d', len(rendered))
    return rendered


def normalize_items(items: List[Any]) -> List[dict]:
    """
    Normalizes a list of input items for prompt generation.

    Ensures each item is a dictionary with `id`, `comment`, and `language` keys.
    - Accepts items that use `comments` instead of `comment`.
    - If `id` is missing, assigns a sequential id starting from 1 for each group.
    - If `language` is a tuple/list (output of detect_lang), it takes the first element.

    Args:
        items (List[Any]): The list of input items to normalize.

    Returns:
        List[dict]: The list of normalized items.
    """
    normalized: List[dict] = []
    for idx, it in enumerate(items, start=1):
        if isinstance(it, dict):
            comment = it.get('comment') or it.get('comments') or ''
            lang = it.get('language')
            idv = it.get('id')
        else:
            comment = str(it)
            lang = None
            idv = None

        if isinstance(lang, (list, tuple)) and len(lang) > 0:
            lang = lang[0]
        if not lang:
            lang = 'und'

        if idv is None or idv == '':
            idv = str(idx)
        else:
            idv = str(idv)

        normalized.append({'id': idv, 'comment': comment, 'language': lang})

    return normalized

