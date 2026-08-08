"""Minimal optional bearer-token guard for hardware-control endpoints.

Behavior:
* When ``API_AUTH_TOKEN`` is empty (default, local demos) every endpoint is open.
* When set, requests to guarded endpoints must send ``Authorization: Bearer <token>``.

No tokens are stored anywhere; the value comes from ``config.API_AUTH_TOKEN``.
"""

from fastapi import HTTPException, Request

import config


def verify_hardware_token(request: Request) -> None:
    """FastAPI dependency rejecting hardware-control requests without the
    configured bearer token. No-op when no token is configured."""
    token = config.API_AUTH_TOKEN
    if not token:
        return

    provided = request.query_params.get("token")
    if provided is None:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            provided = auth_header[7:].strip()

    if provided != token:
        raise HTTPException(status_code=401, detail="Unauthorized")