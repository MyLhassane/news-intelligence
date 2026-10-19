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

    kept_params = []
    for parameter in parts.query.split("&") if parts.query else []:
        if not parameter:
            continue
        if "=" in parameter:
            key, _, value = parameter.partition("=")
            has_equals = True
        else:
            key = parameter
            value = None
            has_equals = False

        decoded_key = unquote_plus(key)

        if decoded_key.casefold() not in TRACKING_PARAMETERS:
            kept_params.append((key, value, has_equals))

    # Group raw parameter strings by key while preserving relative order
    grouped = {}
    key_order = []
    for key, value, has_equals in kept_params:
        if key not in grouped:
            grouped[key] = []
            key_order.append(key)
        grouped[key].append((value, has_equals))

    # Sort distinct keys deterministically based on decoded casefolded key representation
    sorted_keys = sorted(key_order, key=lambda k: unquote_plus(k).casefold())

    sorted_parameters = []
    for k in sorted_keys:
        for v, has_equals in grouped[k]:
            if has_equals:
                sorted_parameters.append(f"{k}={v}" if v is not None else k)
            else:
                sorted_parameters.append(k)

    query = "&".join(sorted_parameters)

    return urlunsplit(
        (
            scheme,
            netloc,
            parts.path or "/",
            query,
            "",
        )
    )
