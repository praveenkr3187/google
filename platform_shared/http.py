import httpx


DEFAULT_TIMEOUT = 60.0


def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
