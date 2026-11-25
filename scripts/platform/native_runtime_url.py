"""URL helpers for the native ROOT-context web runtime."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def application_endpoint_url(base_url: str, endpoint_path: str) -> str:
    """Build an endpoint URL under the deployed ROOT web application.

    The native preview deploys the webapp at Tomcat's ROOT context. Paths such
    as /login and /main are pages inside that context, not context prefixes.
    """
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"URL base inválida para el runtime local: {base_url!r}")

    endpoint = endpoint_path.lstrip("/")
    if not endpoint or "?" in endpoint or "#" in endpoint:
        raise ValueError(f"Ruta de endpoint inválida: {endpoint_path!r}")

    return urlunsplit((parsed.scheme, parsed.netloc, "/" + endpoint, "", ""))
