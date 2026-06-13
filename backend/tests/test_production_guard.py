# test_production_guard.py
# Enforces absolute protection of production database during pytest executions.

import os
import pytest
from unittest.mock import MagicMock, patch

def test_guard_production_url_is_mocked():
    assert os.environ.get('SUPABASE_URL') == 'https://mock-prevent-production-writes.supabase.co'
    assert os.environ.get('SUPABASE_KEY') == 'mock-prevent-production-writes'

def test_guard_create_client_blocks_production_url():
    import supabase
    with pytest.raises(RuntimeError) as excinfo:
        supabase.create_client('https://real-production-project.supabase.co', 'some-real-key')
    assert 'CRITICAL: Accidental production Supabase access blocked' in str(excinfo.value)

def test_guard_main_and_database_use_mock_client():
    try:
        from backend.main import supabase as main_supabase
        from backend.database import supabase as db_supabase
    except ImportError:
        from main import supabase as main_supabase
        from database import supabase as db_supabase

    assert isinstance(main_supabase, MagicMock)
    assert isinstance(db_supabase, MagicMock)

def test_guard_prevent_live_write_operations():
    try:
        from backend.database import supabase as db_supabase
    except ImportError:
        from database import supabase as db_supabase

    table = db_supabase.table('any_table')
    
    res_insert = table.insert({'some': 'data'})
    assert isinstance(res_insert, MagicMock)
    
    res_update = table.update({'some': 'new_data'})
    assert isinstance(res_update, MagicMock)
    
    res_upsert = table.upsert({'some': 'upsert_data'})
    assert isinstance(res_upsert, MagicMock)
    
    res_delete = table.delete()
    assert isinstance(res_delete, MagicMock)

def test_guard_candidate_builder_uses_mock_client():
    from backend.scripts.build_golden_candidates_from_feedback import _get_supabase_client
    client = _get_supabase_client()
    assert isinstance(client, MagicMock)

def test_guard_promoter_uses_mock_client():
    from backend.scripts.promote_golden_candidates import _get_supabase_client
    client = _get_supabase_client()
    assert isinstance(client, MagicMock)

def test_guard_regression_cases_uses_mock_client():
    from backend.scripts.run_golden_oracle_regression_cases import _get_supabase_client
    client = _get_supabase_client()
    assert isinstance(client, MagicMock)
