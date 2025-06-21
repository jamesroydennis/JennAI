# /home/jdennis/Projects/JennAI/src/business/ai/tests/test_ai_response_parser.py

import sys
import pytest
from pathlib import Path
import json

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.business.ai.ai_response_parser import AIResponseParser, AIResponseParsingError
from src.data.obj.min_sys_reqs_dto import MinSysReqsDTO
from pydantic import ValidationError

@pytest.fixture
def ai_response_parser():
    """Provides an instance of AIResponseParser for tests."""
    return AIResponseParser()

def test_parse_response_to_model_valid_json_no_markdown(ai_response_parser: AIResponseParser):
    """Tests successful parsing of valid JSON without markdown."""
    valid_json_response = '{"cpu_cores": 4, "ram_gb": 8.0, "storage_gb": 100.0, "operating_system": ["Linux"], "dependencies": ["Python 3.9"], "notes": "Test notes"}'
    
    parsed_dto = ai_response_parser.parse_response_to_model(valid_json_response, MinSysReqsDTO)
    
    assert isinstance(parsed_dto, MinSysReqsDTO)
    assert parsed_dto.cpu_cores == 4
    assert parsed_dto.ram_gb == 8.0
    assert parsed_dto.storage_gb == 100.0
    assert parsed_dto.operating_system == ["Linux"]
    assert parsed_dto.dependencies == ["Python 3.9"]
    assert parsed_dto.notes == "Test notes"

def test_parse_response_to_model_valid_json_all_fields_populated(ai_response_parser: AIResponseParser):
    """Tests successful parsing of valid JSON with all optional fields populated."""
    full_json_response = '''
    {
      "cpu_cores": 8,
      "ram_gb": 16.0,
      "storage_gb": 250.0,
      "operating_system": ["Windows 11 Pro", "Ubuntu 22.04 LTS"],
      "dependencies": ["Node.js 18+", "Docker 24.0.0", "PostgreSQL 14"],
      "notes": "Requires a stable internet connection for initial setup."
    }
    '''
    parsed_dto = ai_response_parser.parse_response_to_model(full_json_response, MinSysReqsDTO)
    
    assert isinstance(parsed_dto, MinSysReqsDTO)
    assert parsed_dto.cpu_cores == 8
    assert parsed_dto.ram_gb == 16.0
    assert parsed_dto.storage_gb == 250.0
    assert parsed_dto.operating_system == ["Windows 11 Pro", "Ubuntu 22.04 LTS"]
    assert parsed_dto.dependencies == ["Node.js 18+", "Docker 24.0.0", "PostgreSQL 14"]
    assert parsed_dto.notes == "Requires a stable internet connection for initial setup."

def test_parse_response_to_model_valid_json_empty_optional_fields(ai_response_parser: AIResponseParser):
    """Tests successful parsing of valid JSON with optional fields as None or empty lists."""
    empty_optional_json = '''
    {
      "cpu_cores": 1,
      "ram_gb": 2.0,
      "storage_gb": 10.0,
      "operating_system": [],
      "dependencies": null,
      "notes": ""
    }
    '''
    parsed_dto = ai_response_parser.parse_response_to_model(empty_optional_json, MinSysReqsDTO)
    
    assert isinstance(parsed_dto, MinSysReqsDTO)
    assert parsed_dto.cpu_cores == 1
    assert parsed_dto.ram_gb == 2.0
    assert parsed_dto.storage_gb == 10.0
    assert parsed_dto.operating_system == []
    assert parsed_dto.dependencies is None
    assert parsed_dto.notes == ""

def test_parse_response_to_model_valid_json_with_markdown(ai_response_parser: AIResponseParser):
    """Tests successful parsing of valid JSON embedded in markdown."""
    valid_json_response_md = 'Some introductory text.\n```json\n{"cpu_cores": 2, "ram_gb": 4.0, "storage_gb": 50.0}\n```\nSome concluding remarks.'
    
    parsed_dto = ai_response_parser.parse_response_to_model(valid_json_response_md, MinSysReqsDTO)
    
    assert isinstance(parsed_dto, MinSysReqsDTO)
    assert parsed_dto.cpu_cores == 2
    assert parsed_dto.ram_gb == 4.0
    assert parsed_dto.storage_gb == 50.0
    assert parsed_dto.operating_system is None
    assert parsed_dto.dependencies is None
    assert parsed_dto.notes is None

def test_parse_response_to_model_valid_json_with_trailing_text(ai_response_parser: AIResponseParser):
    """Tests successful parsing when there's valid JSON followed by extra text."""
    response_with_trailing_text = '```json\n{"cpu_cores": 1, "ram_gb": 2.0, "storage_gb": 10.0}\n```\n\nThank you for your request.'
    parsed_dto = ai_response_parser.parse_response_to_model(response_with_trailing_text, MinSysReqsDTO)
    assert isinstance(parsed_dto, MinSysReqsDTO)
    assert parsed_dto.cpu_cores == 1
    assert parsed_dto.ram_gb == 2.0
    assert parsed_dto.storage_gb == 10.0

def test_parse_response_to_model_invalid_json(ai_response_parser: AIResponseParser):
    """Tests that parsing fails for invalid JSON."""
    invalid_json_response = 'This is not JSON at all.'
    
    with pytest.raises(AIResponseParsingError, match="Could not extract a valid JSON object"):
        ai_response_parser.parse_response_to_model(invalid_json_response, MinSysReqsDTO)

def test_parse_response_to_model_json_schema_mismatch(ai_response_parser: AIResponseParser):
    """Tests that parsing fails for JSON that doesn't match the DTO schema."""
    # Missing required field 'cpu_cores'
    schema_mismatch_json = '{"ram_gb": 8.0, "storage_gb": 100.0}'
    
    with pytest.raises(AIResponseParsingError, match="AI response JSON does not match the expected schema"):
        ai_response_parser.parse_response_to_model(schema_mismatch_json, MinSysReqsDTO)

def test_parse_response_to_model_json_extra_fields_forbidden(ai_response_parser: AIResponseParser):
    """Tests that parsing fails for JSON with extra fields when extra='forbid' is set."""
    extra_fields_json = '{"cpu_cores": 4, "ram_gb": 8.0, "storage_gb": 100.0, "extra_field": "unexpected"}'
    
    with pytest.raises(AIResponseParsingError, match="AI response JSON does not match the expected schema"):
        ai_response_parser.parse_response_to_model(extra_fields_json, MinSysReqsDTO)

def test_parse_response_to_model_empty_response(ai_response_parser: AIResponseParser):
    """Tests that parsing fails for an empty AI response string."""
    empty_response = ""
    
    with pytest.raises(AIResponseParsingError, match="Could not extract a valid JSON object"):
        ai_response_parser.parse_response_to_model(empty_response, MinSysReqsDTO)

def test_parse_response_to_model_invalid_data_type(ai_response_parser: AIResponseParser):
    """Tests that parsing fails for correct field but wrong data type."""
    invalid_type_json = '{"cpu_cores": "four", "ram_gb": 8.0, "storage_gb": 100.0}'
    
    with pytest.raises(AIResponseParsingError, match="AI response JSON does not match the expected schema"):
        ai_response_parser.parse_response_to_model(invalid_type_json, MinSysReqsDTO)

def test_parse_response_to_model_pydantic_constraint_violation(ai_response_parser: AIResponseParser):
    """Tests that parsing fails when a Pydantic field constraint (e.g., gt=0) is violated."""
    # cpu_cores is 0, which violates gt=0 constraint
    constraint_violation_json = '{"cpu_cores": 0, "ram_gb": 8.0, "storage_gb": 100.0}'
    
    with pytest.raises(AIResponseParsingError, match="AI response JSON does not match the expected schema"):
        ai_response_parser.parse_response_to_model(constraint_violation_json, MinSysReqsDTO)