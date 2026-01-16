"""
Unit tests for TOON parser (toon_to_dicts function)

Tests cover:
- Valid TOON output parsing
- Tolerant parsing (missing fields, extra whitespace)
- Edge cases (empty aspects, malformed lines)
- Multiple aspects per item
"""
import pytest
from app.utils.parsers import toon_to_dicts


class TestToonToDictsBasic:
    """Test basic TOON parsing functionality."""

    def test_parse_single_item_single_aspect(self):
        """Test parsing single item with one aspect."""
        toon = "L:1|screen~positive"
        result = toon_to_dicts(toon)
        
        assert len(result) == 1
        assert result[0]['id'] == '1'
        assert len(result[0]['aspects']) == 1
        assert result[0]['aspects'][0]['term'] == 'screen'
        assert result[0]['aspects'][0]['sentiment'] == 'positive'

    def test_parse_single_item_multiple_aspects(self):
        """Test parsing single item with multiple aspects."""
        toon = "L:1|screen~positive;;battery~negative"
        result = toon_to_dicts(toon)
        
        assert len(result) == 1
        assert len(result[0]['aspects']) == 2
        assert result[0]['aspects'][0]['term'] == 'screen'
        assert result[0]['aspects'][0]['sentiment'] == 'positive'
        assert result[0]['aspects'][1]['term'] == 'battery'
        assert result[0]['aspects'][1]['sentiment'] == 'negative'

    def test_parse_multiple_items(self):
        """Test parsing multiple items."""
        toon = "L:1|screen~positive\nL:2|battery~negative"
        result = toon_to_dicts(toon)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '2'

    def test_parse_neutral_sentiment(self):
        """Test parsing neutral sentiment."""
        toon = "L:1|price~neutral"
        result = toon_to_dicts(toon)
        
        assert result[0]['aspects'][0]['sentiment'] == 'neutral'


class TestToonToDictsEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_empty_string(self):
        """Test parsing empty input."""
        result = toon_to_dicts("")
        assert result == []

    def test_parse_no_l_lines(self):
        """Test input with no L: lines."""
        toon = "Some random text\nAnother line"
        result = toon_to_dicts(toon)
        assert result == []

    def test_parse_empty_aspects(self):
        """Test item with no aspects (empty after |)."""
        toon = "L:1|"
        result = toon_to_dicts(toon)
        
        assert len(result) == 1
        assert result[0]['id'] == '1'
        assert len(result[0]['aspects']) == 0

    def test_parse_whitespace_only_aspects(self):
        """Test aspects part with only whitespace."""
        toon = "L:1|   "
        result = toon_to_dicts(toon)
        
        assert len(result[0]['aspects']) == 0

    def test_parse_extra_whitespace(self):
        """Test tolerance to extra whitespace."""
        toon = "L:1  |  screen ~ positive  ;;  battery ~ negative  "
        result = toon_to_dicts(toon)
        
        assert len(result[0]['aspects']) == 2
        assert result[0]['aspects'][0]['term'] == 'screen'
        assert result[0]['aspects'][1]['term'] == 'battery'

    def test_parse_blank_lines(self):
        """Test tolerance to blank lines."""
        toon = "L:1|screen~positive\n\n\nL:2|battery~negative\n"
        result = toon_to_dicts(toon)
        
        assert len(result) == 2

    def test_parse_lines_without_pipe(self):
        """Test L: lines without pipe separator."""
        toon = "L:1\nL:2|screen~positive"
        result = toon_to_dicts(toon)
        
        # First line should be skipped (no pipe)
        assert len(result) == 1
        assert result[0]['id'] == '2'


class TestToonToDictsTolerance:
    """Test tolerant parsing of malformed input."""

    def test_parse_missing_sentiment(self):
        """Test aspect with only term (no sentiment)."""
        toon = "L:1|screen"
        result = toon_to_dicts(toon)
        
        # Should skip aspect with only one part
        assert len(result[0]['aspects']) == 0

    def test_parse_extra_tilde_parts(self):
        """Test aspect with more than 2 parts (term~sent~extra)."""
        toon = "L:1|screen~positive~extra"
        result = toon_to_dicts(toon)
        
        # Should take first two parts
        assert len(result[0]['aspects']) == 1
        assert result[0]['aspects'][0]['term'] == 'screen'
        assert result[0]['aspects'][0]['sentiment'] == 'positive'

    def test_parse_empty_aspect_between_delimiters(self):
        """Test empty aspect between ;; delimiters."""
        toon = "L:1|screen~positive;;;;battery~negative"
        result = toon_to_dicts(toon)
        
        # Empty aspects should be skipped
        assert len(result[0]['aspects']) == 2

    def test_parse_mixed_valid_invalid_aspects(self):
        """Test line with mix of valid and invalid aspects."""
        toon = "L:1|valid~positive;;invalid;;also~negative"
        result = toon_to_dicts(toon)
        
        assert len(result[0]['aspects']) == 2
        assert result[0]['aspects'][0]['term'] == 'valid'
        assert result[0]['aspects'][1]['term'] == 'also'

    def test_parse_turkish_characters(self):
        """Test parsing Turkish terms and text."""
        toon = "L:1|ekran~pozitif;;batarya~negatif"
        result = toon_to_dicts(toon)
        
        assert result[0]['aspects'][0]['term'] == 'ekran'
        assert result[0]['aspects'][1]['term'] == 'batarya'

    def test_parse_special_characters_in_terms(self):
        """Test terms with special characters."""
        toon = "L:1|user-interface~positive;;price/quality~negative"
        result = toon_to_dicts(toon)
        
        assert len(result[0]['aspects']) == 2
        assert result[0]['aspects'][0]['term'] == 'user-interface'
        assert result[0]['aspects'][1]['term'] == 'price/quality'


class TestToonToDictsRealWorld:
    """Test with realistic LLM outputs."""

    def test_parse_real_world_example_1(self):
        """Test realistic output format."""
        toon = """L:1|screen~positive;;battery~positive
L:2|apps~negative;;UI~negative"""
        result = toon_to_dicts(toon)
        
        assert len(result) == 2
        assert len(result[0]['aspects']) == 2
        assert len(result[1]['aspects']) == 2

    def test_parse_with_commentary_lines(self):
        """Test ignoring non-L: commentary lines."""
        toon = """Here are the results:
L:1|screen~positive
L:2|battery~negative
Done."""
        result = toon_to_dicts(toon)
        
        assert len(result) == 2

    def test_parse_mixed_sentiments(self):
        """Test all three sentiment types in one output."""
        toon = "L:1|good~positive;;bad~negative;;okay~neutral"
        result = toon_to_dicts(toon)
        
        aspects = result[0]['aspects']
        sentiments = [a['sentiment'] for a in aspects]
        assert 'positive' in sentiments
        assert 'negative' in sentiments
        assert 'neutral' in sentiments

    def test_parse_numeric_ids(self):
        """Test numeric IDs are preserved as strings."""
        toon = "L:42|test~positive"
        result = toon_to_dicts(toon)
        
        assert result[0]['id'] == '42'
        assert isinstance(result[0]['id'], str)

    def test_parse_batch_output(self):
        """Test parsing a full batch response."""
        toon = """L:1|design~positive;;price~negative
L:2|performance~positive;;noise~negative;;weight~neutral
L:3|quality~positive"""
        result = toon_to_dicts(toon)
        
        assert len(result) == 3
        assert len(result[0]['aspects']) == 2
        assert len(result[1]['aspects']) == 3
        assert len(result[2]['aspects']) == 1


class TestToonToDictsReturnStructure:
    """Test the structure of returned dictionaries."""

    def test_return_type(self):
        """Test that function returns list of dicts."""
        toon = "L:1|test~positive"
        result = toon_to_dicts(toon)
        
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

    def test_item_keys(self):
        """Test that each item has required keys."""
        toon = "L:1|test~positive"
        result = toon_to_dicts(toon)
        
        assert 'id' in result[0]
        assert 'aspects' in result[0]

    def test_aspect_keys(self):
        """Test that each aspect has required keys."""
        toon = "L:1|test~positive"
        result = toon_to_dicts(toon)
        
        aspect = result[0]['aspects'][0]
        assert 'term' in aspect
        assert 'sentiment' in aspect
        assert len(aspect) == 2  # Only term and sentiment

    def test_aspects_is_list(self):
        """Test that aspects is always a list."""
        toon = "L:1|test~positive"
        result = toon_to_dicts(toon)
        
        assert isinstance(result[0]['aspects'], list)
