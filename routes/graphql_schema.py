"""Optional GraphQL schema scaffolding.

If `strawberry` is available, exposes a minimal schema for health checks.
Otherwise, provides helpers that indicate GraphQL is not configured.
"""

from typing import Any

try:
    import strawberry
    from strawberry.fastapi import GraphQLRouter

    @strawberry.type
    class Query:
        status: str = "ok"

    schema = strawberry.Schema(query=Query)

    def get_graphql_router() -> Any:
        return GraphQLRouter(schema)
except Exception:
    schema = None

    def get_graphql_router() -> Any:
        return None