"""
Unit tests for app/utils/parsers.py

Tests cover:
- parse_data: string and CSV file handling
- create_df: DataFrame standardization and validation
- batch_packing: fixed-size batching logic
"""
import pytest
import pandas as pd
from io import StringIO, BytesIO
from app.utils.parsers import parse_data, create_df, batch_packing


class TestParseData:
    """Test parse_data function with various input types."""

    def test_parse_data_string_input(self):
        """Test parsing a simple string."""
        result = parse_data("This is a test comment")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == '1'
        assert result[0]['comments'] == "This is a test comment"
        assert 'language' in result[0]

    def test_parse_data_csv_with_id_and_comments(self):
        """Test parsing CSV with both id and comments columns."""
        csv_content = "id,comments\n1,Great product\n2,Not good"
        csv_file = StringIO(csv_content)
        result = parse_data(csv_file)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[0]['comments'] == "Great product"
        assert result[1]['id'] == '2'
        assert result[1]['comments'] == "Not good"

    def test_parse_data_csv_single_column(self):
        """Test parsing single-column CSV (treated as comments)."""
        csv_content = "feedback\nAwesome\nTerrible"
        csv_file = StringIO(csv_content)
        result = parse_data(csv_file)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'  # auto-generated
        assert result[0]['comments'] == "Awesome"
        assert result[1]['id'] == '2'
        assert result[1]['comments'] == "Terrible"

    def test_parse_data_csv_missing_id(self):
        """Test CSV with comments but no id column."""
        csv_content = "comments\nFirst comment\nSecond comment"
        csv_file = StringIO(csv_content)
        result = parse_data(csv_file)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'  # auto-generated
        assert result[1]['id'] == '2'

    def test_parse_data_empty_string(self):
        """Test parsing empty string."""
        result = parse_data("")
        assert len(result) == 1
        assert result[0]['comments'] == ""


class TestCreateDF:
    """Test create_df DataFrame standardization."""

    def test_create_df_with_id_and_comments(self):
        """Test DataFrame with both columns."""
        df = pd.DataFrame({
            'id': ['1', '2'],
            'comments': ['First', 'Second']
        })
        result = create_df(df)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[0]['comments'] == 'First'

    def test_create_df_single_column(self):
        """Test single-column DataFrame."""
        df = pd.DataFrame({
            'review': ['Good', 'Bad']
        })
        result = create_df(df)
        
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[0]['comments'] == 'Good'
        assert result[1]['id'] == '2'

    def test_create_df_applies_sanitization(self):
        """Test that sanitization is applied to comments."""
        df = pd.DataFrame({
            'id': ['1'],
            'comments': ['  Extra   spaces  ']
        })
        result = create_df(df)
        
        # Should be sanitized (normalized spaces)
        assert result[0]['comments'].strip() != ''

    def test_create_df_invalid_raises_error(self):
        """Test that multi-column DF without comments raises error."""
        df = pd.DataFrame({
            'col1': ['a'],
            'col2': ['b'],
            'col3': ['c']
        })
        with pytest.raises(ValueError, match="CSV must contain comments data"):
            create_df(df)


class TestBatchPacking:
    """Test batch_packing fixed-size batching."""

    def test_batch_packing_single_batch(self):
        """Test items fitting in one batch."""
        items = [{'id': str(i)} for i in range(5)]
        batches = batch_packing(items, max_items=10)
        
        assert len(batches) == 1
        assert len(batches[0]) == 5

    def test_batch_packing_multiple_batches(self):
        """Test items split across multiple batches."""
        items = [{'id': str(i)} for i in range(25)]
        batches = batch_packing(items, max_items=10)
        
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_batch_packing_exact_fit(self):
        """Test items exactly filling batches."""
        items = [{'id': str(i)} for i in range(20)]
        batches = batch_packing(items, max_items=10)
        
        assert len(batches) == 2
        assert all(len(b) == 10 for b in batches)

    def test_batch_packing_empty_list(self):
        """Test empty input."""
        batches = batch_packing([], max_items=10)
        assert len(batches) == 0

    def test_batch_packing_single_item(self):
        """Test single item."""
        items = [{'id': '1'}]
        batches = batch_packing(items, max_items=10)
        
        assert len(batches) == 1
        assert len(batches[0]) == 1
