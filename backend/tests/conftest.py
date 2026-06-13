import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ==========================================
# ABSOLUTE PYTEST PRODUCTION GUARD
# ==========================================

# 1. Block dotenv from loading production .env file
import dotenv
def mock_load_dotenv(*args, **kwargs):
    return True
dotenv.load_dotenv = mock_load_dotenv

# 2. Force fake/mock environment variables
os.environ["SUPABASE_URL"] = "https://mock-prevent-production-writes.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-prevent-production-writes"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock-prevent-production-writes"

# 3. Mock supabase.create_client to return a secure Mock client
import supabase
from unittest.mock import MagicMock

def mock_create_client(supabase_url: str, supabase_key: str, *args, **kwargs):
    # Prevent execution with production URL/credentials
    if "prevent-production" not in supabase_url:
        raise RuntimeError(f"CRITICAL: Accidental production Supabase access blocked! URL: {supabase_url}")
    
    mock_client = MagicMock()
    # Configure default mock return values so that chained calls do not fail
    mock_table = MagicMock()
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.in_.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[])
    
    mock_client.table.return_value = mock_table
    return mock_client

supabase.create_client = mock_create_client
