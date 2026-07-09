"""Database storage for user contracts using team-db CLI."""

import json
import os
import uuid
import subprocess
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


TEAM_DB_CMD = os.environ.get(
    "TEAM_DB_CMD",
    "/home/agent-ai-ml-engineer/.local/bin/team-db"
)

# Flag to track if team-db is available
_team_db_available: Optional[bool] = None


def _check_team_db() -> bool:
    """Check if the team-db CLI is available."""
    global _team_db_available
    if _team_db_available is not None:
        return _team_db_available
    try:
        subprocess.run([TEAM_DB_CMD, "--help"], capture_output=True, timeout=5)
        _team_db_available = True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        _team_db_available = False
    return _team_db_available


def _run_sql(sql: str) -> List[Dict[str, Any]]:
    """Execute SQL via team-db CLI and return parsed JSON results."""
    if not _check_team_db():
        return []
    try:
        result = subprocess.run(
            [TEAM_DB_CMD, sql],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"team-db error: {result.stderr.strip()}")
            return []
        output = result.stdout.strip()
        if output:
            return json.loads(output)
        return []
    except FileNotFoundError:
        print(f"team-db CLI not found at {TEAM_DB_CMD}")
        return []
    except json.JSONDecodeError:
        return []
    except subprocess.TimeoutExpired:
        print("team-db query timed out")
        return []
    except Exception as e:
        print(f"team-db error: {e}")
        return []


def init_db():
    """Create the contracts table if it doesn't exist."""
    _run_sql(
        "CREATE TABLE IF NOT EXISTS contracts "
        "(id TEXT PRIMARY KEY, clerk_user_id TEXT NOT NULL, "
        "filename TEXT NOT NULL, analysis_json TEXT NOT NULL, "
        "created_at TEXT NOT NULL)"
    )


def save_contract(clerk_user_id: str, filename: str, analysis_result: Dict[str, Any]) -> str:
    """
    Save an analysis result to the database.
    
    Returns the generated contract ID.
    """
    contract_id = str(uuid.uuid4())[:12]
    created_at = datetime.now(timezone.utc).isoformat()
    analysis_json = json.dumps(analysis_result, default=str)

    sql = (
        f"INSERT INTO contracts (id, clerk_user_id, filename, analysis_json, created_at) "
        f"VALUES ('{contract_id}', '{clerk_user_id}', "
        f"'{filename.replace(chr(39), chr(39)+chr(39))}', "
        f"'{analysis_json.replace(chr(39), chr(39)+chr(39))}', "
        f"'{created_at}')"
    )
    _run_sql(sql)
    return contract_id


def get_user_contracts(clerk_user_id: str) -> List[Dict[str, Any]]:
    """
    Return a list of contracts for a user.
    
    Returns summary info (id, filename, created_at) without full analysis JSON.
    """
    sql = (
        f"SELECT id, filename, created_at FROM contracts "
        f"WHERE clerk_user_id = '{clerk_user_id}' "
        f"ORDER BY created_at DESC"
    )
    rows = _run_sql(sql)
    return rows


def get_contract(contract_id: str, clerk_user_id: str) -> Optional[Dict[str, Any]]:
    """
    Return a single contract with ownership verification.
    
    Returns None if not found or not owned by the user.
    """
    sql = (
        f"SELECT id, clerk_user_id, filename, analysis_json, created_at "
        f"FROM contracts WHERE id = '{contract_id}'"
    )
    rows = _run_sql(sql)
    if not rows:
        return None

    contract = rows[0]
    # Verify ownership
    if contract.get("clerk_user_id") != clerk_user_id:
        return None

    # Parse analysis_json back to dict
    if isinstance(contract.get("analysis_json"), str):
        try:
            contract["analysis_json"] = json.loads(contract["analysis_json"])
        except (json.JSONDecodeError, TypeError):
            pass

    return contract