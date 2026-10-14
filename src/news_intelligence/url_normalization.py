from urllib.parse import unquote_plus, urlsplit, urlunsplit

TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gclid",
    "dclid",
    "fbclid",
}


def normalize_url(url: str) -> str:
    if not url or not url.strip():
        raise ValueError("url must not be empty")

    url = url.strip()
    parts = urlsplit(url)

    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"}:
        raise ValueError("url must use HTTP or HTTPS")

    if not parts.hostname:
        raise ValueError("url must include a hostname")

    if parts.username is not None or parts.password is not None:
        raise ValueError("url must not contain credentials")

    hostname = parts.hostname.lower()

    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("url contains an invalid port") from exc

    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"

    netloc = hostname
    if port is not None and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        netloc = f"{netloc}:{port}"

    kept_parameters = []
    for parameter in parts.query.split("&") if parts.query else []:
        key = parameter.partition("=")[0]
        decoded_key = unquote_plus(key)

        if decoded_key.casefold() not in TRACKING_PARAMETERS:
            kept_parameters.append(parameter)

    query = "&".join(kept_parameters)

    return urlunsplit(
        (
            scheme,
            netloc,
            parts.path or "/",
            query,
            "",
        )
    )
