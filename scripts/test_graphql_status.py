"""GraphQL schema smoke: ensure schema executes the status query."""
from routes.graphql_schema import schema

def main():
    result = schema.execute_sync("{ status }")
    assert result and not result.errors, f"GraphQL errors: {result.errors}"
    assert result.data.get('status') == 'ok'
    print('GraphQL schema status OK')

if __name__ == '__main__':
    main()

