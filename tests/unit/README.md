# Unit Tests

Modüler birim test yapısı — kritik fonksiyonları test eder.

## Yapı

```
tests/
├── conftest.py              # Pytest configuration
└── unit/                    # Unit tests (fast, isolated)
    ├── __init__.py
    ├── test_parsers.py      # Parsers: parse_data, batch_packing, etc.
    ├── test_sanitizer.py    # Sanitizer: sanitize_comment, normalization
    ├── test_manager.py      # Prompt manager: normalize_items, render
    └── test_toon_parser.py  # TOON parser: toon_to_dicts
```

## Testleri Çalıştırma

### Tüm unit testler
```powershell
pytest tests/unit/ -v
```

### Belirli bir modül
```powershell
pytest tests/unit/test_parsers.py -v
pytest tests/unit/test_toon_parser.py -v
```

### Coverage ile
```powershell
pytest tests/unit/ --cov=app --cov-report=html
```

### Hızlı (sadece işaretlenmiş unit testler)
```powershell
pytest tests/unit/ -m unit -v
```

## Test Kapsamı

### 1. Parsers (`test_parsers.py`)
- ✅ `parse_data`: string, CSV file-like objelerini parse etme
- ✅ `create_df`: DataFrame standardizasyonu ve validasyon
- ✅ `batch_packing`: sabit boyutlu batch oluşturma
- Edge cases: tek sütun, eksik id, boş girdi

### 2. Sanitizer (`test_sanitizer.py`)
- ✅ `sanitize_comment`: tam pipeline (normalize + truncate + escape)
- ✅ `_normalize_comment`: Unicode, whitespace, newline normalizasyonu
- ✅ `_truncate_comment`: kelime sınırında kısaltma
- ✅ `_escape_delimiters`: L: ve kontrol karakteri escapeleme
- Edge cases: çok uzun metin, özel karakterler, Unicode

### 3. Prompt Manager (`test_manager.py`)
- ✅ `normalize_items`: `comment`/`comments` mapping, dil tuple handling, id oluşturma
- ✅ `load_prompt`: YAML prompt yükleme
- ✅ `render`: Jinja2 template rendering
- Integration: normalize + render pipeline

### 4. TOON Parser (`test_toon_parser.py`)
- ✅ `toon_to_dicts`: TOON formatını dict listesine parse
- ✅ Tolerant parsing: boş satırlar, eksik alanlar, extra whitespace
- ✅ Edge cases: boş aspects, malformed lines, özel karakterler
- ✅ Gerçek dünya senaryoları: batch çıktılar, mixed sentiments

## Test Yazma Kuralları

1. **İzolasyon**: Her test bağımsız olmalı (shared state yok)
2. **Açıklayıcı İsimler**: `test_function_behavior_expected`
3. **AAA Pattern**: Arrange → Act → Assert
4. **Edge Cases**: Sınır değerleri, boş girdi, hatalı formatlar
5. **Markers**: `@pytest.mark.unit` veya `@pytest.mark.integration`

## Örnek Test Çalıştırma

```powershell
# Hızlı smoke test
pytest tests/unit/test_toon_parser.py::TestToonToDictsBasic::test_parse_single_item_single_aspect -v

# Tüm TOON parser testleri
pytest tests/unit/test_toon_parser.py -v

# Verbose + detailed output
pytest tests/unit/ -vv --tb=short

# Fail durunda hemen dur
pytest tests/unit/ -x
```

## Beklenen Coverage

| Modül | Hedef Coverage | Kritik Fonksiyonlar |
|-------|---------------|---------------------|
| parsers.py | 85%+ | parse_data, toon_to_dicts, batch_packing |
| sanitizer.py | 90%+ | sanitize_comment, tüm yardımcılar |
| manager.py | 80%+ | normalize_items, render |
| absa_service.py | 60%+ | analyze_items (kısmi, integration ağırlıklı) |

## Bağımlılıklar

```bash
pip install pytest pytest-cov pytest-asyncio
```

## CI/CD Entegrasyonu

GitHub Actions örneği:
```yaml
- name: Run unit tests
  run: |
    pytest tests/unit/ -v --cov=app --cov-report=xml
```
