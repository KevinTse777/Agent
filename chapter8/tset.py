import os
from urllib.parse import urlparse

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException


def build_url_candidates(raw_url: str) -> list[str]:
    url = raw_url.strip().rstrip("/")
    candidates = [url]
    parsed = urlparse(url)

    # Some Qdrant Cloud clusters work better on default HTTPS port 443.
    if parsed.scheme == "https" and parsed.port == 6333:
        no_port = f"{parsed.scheme}://{parsed.hostname}"
        if no_port not in candidates:
            candidates.append(no_port)
    return candidates


def main() -> None:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        raise ValueError(
            "Please set QDRANT_URL and QDRANT_API_KEY environment variables."
        )

    last_exc = None
    for url in build_url_candidates(qdrant_url):
        try:
            client = QdrantClient(url=url, api_key=qdrant_api_key)
            collections = client.get_collections()
            print(f"Connected to: {url}")
            print(collections)
            return
        except ResponseHandlingException as exc:
            last_exc = exc
            print(f"Connection failed for {url}: {exc}")

    raise RuntimeError(f"All Qdrant connection attempts failed. Last error: {last_exc}")


if __name__ == "__main__":
    main()
