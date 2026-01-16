"""
Unit tests for app/prompting/manager.py

Tests cover:
- normalize_items: item normalization for template rendering
- load_prompt: prompt file loading
- render: template rendering with items
"""
import pytest
from pathlib import Path
from app.prompting.manager import normalize_items, load_prompt, render


class TestNormalizeItems:
    """Test normalize_items function."""

    def test_normalize_basic_dict(self):
        """Test normalizing basic dict items."""
        items = [
            {'id': '1', 'comment': 'Test', 'language': 'en'}
        ]
        result = normalize_items(items)
        
        assert len(result) == 1
        assert result[0]['id'] == '1'
        assert result[0]['comment'] == 'Test'
        assert result[0]['language'] == 'en'

    def test_normalize_comments_to_comment(self):
        """Test 'comments' key is mapped to 'comment'."""
        items = [
            {'id': '1', 'comments': 'Test comment', 'language': 'en'}
        ]
        result = normalize_items(items)
        
        assert result[0]['comment'] == 'Test comment'
        assert 'comments' not in result[0]

    def test_normalize_missing_id(self):
        """Test auto-generation of missing ids."""
        items = [
            {'comment': 'First'},
            {'comment': 'Second'},
            {'comment': 'Third'}
        ]
        result = normalize_items(items)
        
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '2'
        assert result[2]['id'] == '3'

    def test_normalize_language_tuple(self):
        """Test language tuple/list is converted to first element."""
        items = [
            {'id': '1', 'comment': 'Test', 'language': ('en', 0.95)}
        ]
        result = normalize_items(items)
        
        assert result[0]['language'] == 'en'

    def test_normalize_language_list(self):
        """Test language list handling."""
        items = [
            {'id': '1', 'comment': 'Test', 'language': ['tr', 0.9]}
        ]
        result = normalize_items(items)
        
        assert result[0]['language'] == 'tr'

    def test_normalize_missing_language(self):
        """Test default language when missing."""
        items = [
            {'id': '1', 'comment': 'Test'}
        ]
        result = normalize_items(items)
        
        assert result[0]['language'] == 'und'

    def test_normalize_empty_id(self):
        """Test empty string id is replaced."""
        items = [
            {'id': '', 'comment': 'Test'}
        ]
        result = normalize_items(items)
        
        assert result[0]['id'] == '1'

    def test_normalize_string_item(self):
        """Test that string items are converted to dict."""
        items = ['Test comment']
        result = normalize_items(items)
        
        assert isinstance(result[0], dict)
        assert result[0]['comment'] == 'Test comment'
        assert result[0]['id'] == '1'

    def test_normalize_mixed_items(self):
        """Test normalizing mixed dict and missing fields."""
        items = [
            {'id': '10', 'comment': 'Has ID', 'language': 'en'},
            {'comment': 'No ID', 'language': ('tr', 0.8)},
            {'id': '30', 'comments': 'Uses comments key'}
        ]
        result = normalize_items(items)
        
        assert result[0]['id'] == '10'
        assert result[1]['id'] == '2'
        assert result[1]['language'] == 'tr'
        assert result[2]['comment'] == 'Uses comments key'

    def test_normalize_empty_list(self):
        """Test empty input list."""
        result = normalize_items([])
        assert result == []


class TestLoadPrompt:
    """Test load_prompt function."""

    def test_load_prompt_valid_file(self):
        """Test loading a valid prompt YAML file."""
        # Use the actual absa_v1.yaml from the project
        prompt_path = "app/prompts/absa_v1.yaml"
        result = load_prompt(prompt_path)
        
        assert isinstance(result, dict)
        assert 'meta' in result or 'template' in result
        assert result['template'] is not None

    def test_load_prompt_has_template(self):
        """Test that loaded prompt contains template field."""
        prompt_path = "app/prompts/absa_v1.yaml"
        result = load_prompt(prompt_path)
        
        assert 'template' in result
        assert isinstance(result['template'], str)
        assert len(result['template']) > 0

    def test_load_prompt_nonexistent_file(self):
        """Test that nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_prompt.yaml")


class TestRender:
    """Test render function."""

    def test_render_basic_template(self):
        """Test rendering with basic items."""
        prompt_path = "app/prompts/absa_v1.yaml"
        items = [
            {'id': '1', 'comment': 'Great product', 'language': 'en'},
            {'id': '2', 'comment': 'Not good', 'language': 'en'}
        ]
        
        result = render(prompt_path, items)
        
        assert isinstance(result, str)
        assert 'U:1|Great product|en' in result
        assert 'U:2|Not good|en' in result

    def test_render_single_item(self):
        """Test rendering with single item."""
        prompt_path = "app/prompts/absa_v1.yaml"
        items = [
            {'id': '1', 'comment': 'Test', 'language': 'tr'}
        ]
        
        result = render(prompt_path, items)
        
        assert 'U:1|Test|tr' in result

    def test_render_empty_items(self):
        """Test rendering with empty items list."""
        prompt_path = "app/prompts/absa_v1.yaml"
        result = render(prompt_path, [])
        
        assert isinstance(result, str)
        # Template header should still be present
        assert 'TOON ABSA' in result or 'L:' in result

    def test_render_special_characters(self):
        """Test rendering with special characters in comments."""
        prompt_path = "app/prompts/absa_v1.yaml"
        items = [
            {'id': '1', 'comment': 'Test & special | chars', 'language': 'en'}
        ]
        
        result = render(prompt_path, items)
        
        assert 'U:1|' in result
        assert isinstance(result, str)

    def test_render_turkish_text(self):
        """Test rendering Turkish characters."""
        prompt_path = "app/prompts/absa_v1.yaml"
        items = [
            {'id': '1', 'comment': 'Çok güzel ürün', 'language': 'tr'}
        ]
        
        result = render(prompt_path, items)
        
        assert 'U:1|Çok güzel ürün|tr' in result


class TestIntegration:
    """Integration tests for normalize + render pipeline."""

    def test_normalize_and_render_pipeline(self):
        """Test complete pipeline from raw items to rendered prompt."""
        raw_items = [
            {'comments': 'First comment', 'language': ('en', 0.9)},
            {'id': '5', 'comment': 'Second comment'}
        ]
        
        normalized = normalize_items(raw_items)
        result = render("app/prompts/absa_v1.yaml", normalized)
        
        assert 'U:1|First comment|en' in result
        assert 'U:5|Second comment|und' in result
