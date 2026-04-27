"""CLI entry point.

Usage:
    gh-query "natural language query"                    # NL → LLM → GraphQL → API
    gh-query --model gemini-3.1-flash-lite-preview "..."
    gh-query --raw 'query { viewer { login } }'          # bypass LLM; execute GraphQL directly
"""

import json
import os
import sys
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv

from gh_query.github import GitHubAPIError, execute_graphql
from gh_query.llm import LLMError, call_llm


load_dotenv()

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def query(
    nl: Annotated[
        Optional[str],
        typer.Argument(help="Natural language question. Omit when using --raw."),
    ] = None,
    model: Annotated[
        str, typer.Option(help="LLM model identifier.")
    ] = "gpt-5.4-mini",
    show_query: Annotated[
        bool, typer.Option("--show-query", help="Print the generated GraphQL to stderr.")
    ] = False,
    raw: Annotated[
        Optional[str],
        typer.Option(
            "--raw",
            "-r",
            help="Bypass the LLM and send this GraphQL string directly to GitHub.",
        ),
    ] = None,
) -> None:
    """Convert NL to GitHub GraphQL, execute, and print JSON result."""
    if raw is not None and nl is not None:
        _fail("Use either NL argument or --raw, not both", code=2)
    if raw is None and (nl is None or not nl.strip()):
        _fail("input cannot be empty (provide NL argument or --raw)", code=2)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        _fail("GITHUB_TOKEN not set in environment", code=2)

    if raw is not None:
        graphql = raw
    else:
        try:
            graphql = call_llm(model, nl)
        except LLMError as e:
            _fail(f"LLM call failed: {e}", code=1)

    if show_query:
        print(graphql, file=sys.stderr)

    try:
        data = execute_graphql(graphql, token)
    except GitHubAPIError as e:
        _fail(f"GitHub API error: {e}", code=1)

    print(json.dumps(data, indent=2, ensure_ascii=False))


def _fail(message: str, code: int) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
