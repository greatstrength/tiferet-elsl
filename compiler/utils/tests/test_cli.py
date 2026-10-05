"""Utils – Compiler CLI Entry Tests"""

# *** imports

# ** app
from ...cli import rewrite_asset_paths

# *** tests

# ** test: rewrite_asset_paths_rewrites_prefix
def test_rewrite_asset_paths_rewrites_prefix() -> None:
    '''
    Test that catalog asset prefixes are rewritten and unrelated strings are not.
    '''

    # Only strings that start with the catalog prefix change.
    rewritten = rewrite_asset_paths(
        {
            'const': {'token_config': 'compiler/assets/tokens.yml'},
            'name': 'compiler',
        },
        '/pkg/assets',
    )
    assert rewritten == {
        'const': {'token_config': '/pkg/assets/tokens.yml'},
        'name': 'compiler',
    }
