"""GitHub GraphQL API client."""

import httpx


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns errors or non-2xx status."""


def execute_graphql(query: str, token: str, timeout: float = 30.0) -> dict:
    """Execute a GraphQL query against the GitHub API.

    Returns the `data` field on success.
    Raises GitHubAPIError on HTTP error or when the response contains `errors`.
    """
    response = httpx.post(
        GITHUB_GRAPHQL_URL,
        headers={
            "Authorization": f"bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"query": query},
        timeout=timeout,
    )

    if response.status_code != 200:
        raise GitHubAPIError(
            f"HTTP {response.status_code}: {response.text}"
        )

    body = response.json()
    if "errors" in body:
        raise GitHubAPIError(f"GraphQL errors: {body['errors']}")

    return body.get("data", {})
