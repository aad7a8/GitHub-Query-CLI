"""GitHub GraphQL API client + fixed search template.

The outer GraphQL is a fixed template — `search_query` is passed in as a
GraphQL variable, never string-interpolated. This is ADR-02's "Python
template + LLM-only-inner-DSL" architecture.
"""

import httpx

from gh_query.llm import SearchParams


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


# Fixed template. Fragments cover all 6 entity types reachable via search()
# (Repository / Issue / PullRequest / User / Organization / Discussion).
# Unused fragments are no-ops at the GraphQL layer when their type doesn't
# appear in the union response.
SEARCH_TEMPLATE = """
query GhSearch($q: String!, $t: SearchType!, $n: Int!) {
  search(query: $q, type: $t, first: $n) {
    repositoryCount
    issueCount
    userCount
    discussionCount
    nodes {
      ... on Repository {
        nameWithOwner
        description
        url
        stargazerCount
        forkCount
        pushedAt
        isArchived
        primaryLanguage { name }
        licenseInfo { spdxId name }
      }
      ... on Issue {
        number
        title
        url
        state
        author { login }
        repository { nameWithOwner }
        createdAt
        closedAt
      }
      ... on PullRequest {
        number
        title
        url
        state
        merged
        mergedAt
        author { login }
        repository { nameWithOwner }
        createdAt
      }
      ... on User {
        login
        name
        url
        bio
        company
      }
      ... on Organization {
        login
        name
        url
        description
      }
      ... on Discussion {
        number
        title
        url
        repository { nameWithOwner }
        category { name }
        createdAt
      }
    }
  }
}
""".strip()


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns errors or non-2xx status."""


def build_search_graphql(params: SearchParams) -> tuple[str, dict]:
    """Render SearchParams to (graphql_query, variables) for execute_graphql."""
    variables = {
        "q": params.search_query,
        "t": params.type,
        "n": params.first,
    }
    return SEARCH_TEMPLATE, variables


def execute_graphql(
    query: str,
    token: str,
    variables: dict | None = None,
    timeout: float = 30.0,
) -> dict:
    """Execute a GraphQL query against the GitHub API.

    Returns the `data` field on success.
    Raises GitHubAPIError on HTTP error or when the response contains `errors`.
    """
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables

    response = httpx.post(
        GITHUB_GRAPHQL_URL,
        headers={
            "Authorization": f"bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json=payload,
        timeout=timeout,
    )

    if response.status_code != 200:
        raise GitHubAPIError(f"HTTP {response.status_code}: {response.text}")

    body = response.json()
    if "errors" in body:
        raise GitHubAPIError(f"GraphQL errors: {body['errors']}")

    return body.get("data", {})
