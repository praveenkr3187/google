from typing import Any, Dict, Optional

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import firestore

from .config import FIRESTORE_COLLECTION, PROJECT_ID


_client: Optional[firestore.Client] = None
_memory_store: Dict[str, Dict[str, Any]] = {}


def get_client() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=PROJECT_ID)
    return _client


def get_context(context_id: str) -> Optional[Dict[str, Any]]:
    if _memory_store:
        return _memory_store.get(context_id)
    try:
        doc = get_client().collection(FIRESTORE_COLLECTION).document(context_id).get()
    except DefaultCredentialsError:
        return _memory_store.get(context_id)
    if not doc.exists:
        return None
    return doc.to_dict()


def upsert_context(context_id: str, data: Dict[str, Any]) -> None:
    try:
        get_client().collection(FIRESTORE_COLLECTION).document(context_id).set(data, merge=True)
    except DefaultCredentialsError:
        existing = _memory_store.get(context_id, {})
        existing.update(data)
        _memory_store[context_id] = existing
