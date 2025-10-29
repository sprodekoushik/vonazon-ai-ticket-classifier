# services/crm.py
from typing import List
import os, json, time
from core.schemas import ClassificationResult

# Write to data/push_log.jsonl (create folder if missing)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_PATH = os.path.join(DATA_DIR, "push_log.jsonl")

os.makedirs(DATA_DIR, exist_ok=True)

def push_to_crm(batch: List[ClassificationResult]) -> int:
    """
    Simulate pushing to a CRM by appending JSON lines.
    Returns the number of records written.
    """
    count = 0
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for r in batch:
            record = {
                "ts": int(time.time()),
                "ticket_id": r.ticket_id,
                "category": r.category,
                "confidence": r.confidence,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count

def log_path() -> str:
    return LOG_PATH
