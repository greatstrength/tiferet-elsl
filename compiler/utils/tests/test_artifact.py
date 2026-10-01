"""Utils – ArtifactBlockParser Tests"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest

# ** app
from ..artifact import ArtifactBlockParser

# *** constants

# ** constant: sample_source
SAMPLE_SOURCE = """# *** imports

# ** core
from typing import Any

# *** events

# ** event: add_item
class AddItem:
    '''Add an item.'''

# ** event: remove_item
class RemoveItem:
    '''Remove an item.'''
"""

# *** fixtures

# ** fixture: sample_lines
@pytest.fixture
def sample_lines() -> List[str]:
    '''
    Fixture for source lines with an imports section and two event artifacts.

    :return: Sample lines with keepends preserved.
    :rtype: List[str]
    '''

    # Keep line endings so block text joins back to the source span.
    return SAMPLE_SOURCE.splitlines(keepends=True)

# *** tests

# ** test: parse_extract_filter_none
def test_parse_extract_filter_none() -> None:
    '''
    Test that a missing extract filter returns None.
    '''

    # Falsy None means no extract filter.
    assert ArtifactBlockParser.parse_extract_filter(None) is None

# ** test: parse_extract_filter_empty_string
def test_parse_extract_filter_empty_string() -> None:
    '''
    Test that an empty extract filter returns None.
    '''

    # An empty string means no extract filter.
    assert ArtifactBlockParser.parse_extract_filter('') is None

# ** test: parse_extract_filter_single
def test_parse_extract_filter_single() -> None:
    '''
    Test that a single extract name is returned as a one-item set.
    '''

    # A single name is preserved as a set.
    assert ArtifactBlockParser.parse_extract_filter('add_item') == {'add_item'}

# ** test: parse_extract_filter_multiple
def test_parse_extract_filter_multiple() -> None:
    '''
    Test that comma-separated extract names are stripped into a set.
    '''

    # Whitespace around names is stripped.
    assert ArtifactBlockParser.parse_extract_filter(
        'add_item, remove_item , get_item',
    ) == {'add_item', 'remove_item', 'get_item'}

# ** test: extract_imports_block_found
def test_extract_imports_block_found(sample_lines: List[str]) -> None:
    '''
    Test that the imports section is returned as an __imports__ block.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # The imports span includes the header and the import line, and stops before events.
    block = ArtifactBlockParser.extract_imports_block(sample_lines)
    assert block['name'] == '__imports__'
    assert '# *** imports' in block['text']
    assert 'from typing import Any' in block['text']
    assert block['length_chars'] == len(block['text'])

# ** test: extract_imports_block_not_found
def test_extract_imports_block_not_found() -> None:
    '''
    Test that lines without an imports section return None.
    '''

    # A construct group alone is not an imports block.
    assert ArtifactBlockParser.extract_imports_block([
        '# *** events\n',
        '# ** event: add_item\n',
    ]) is None

# ** test: extract_group_header_found
def test_extract_group_header_found(sample_lines: List[str]) -> None:
    '''
    Test that the sample group header is the events section.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # The sample's construct group is events.
    block = ArtifactBlockParser.extract_group_header(sample_lines)
    assert block['name'] == '__group_header__'
    assert '# *** events' in block['text']

# ** test: extract_group_header_skips_imports
def test_extract_group_header_skips_imports(sample_lines: List[str]) -> None:
    '''
    Test that the first non-imports top-level section is the group header.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # Imports is skipped even though it is the first top-level section.
    events_index = next(
        i for i, line in enumerate(sample_lines) if line.startswith('# *** events')
    )
    block = ArtifactBlockParser.extract_group_header(sample_lines)
    assert block['line_start'] == events_index
    assert block['line_end'] == events_index + 1
    assert block['text'] == sample_lines[events_index]
    assert 'imports' not in block['text']

# ** test: extract_group_header_not_found
def test_extract_group_header_not_found() -> None:
    '''
    Test that lines without a non-imports top-level section return None.
    '''

    # Imports alone, and lines with no top-level section, are not a group header.
    assert ArtifactBlockParser.extract_group_header([
        '# *** imports\n',
        'from typing import Any\n',
    ]) is None
    assert ArtifactBlockParser.extract_group_header([
        'class AddItem:\n',
    ]) is None

# ** test: extract_artifact_blocks_events
def test_extract_artifact_blocks_events(sample_lines: List[str]) -> None:
    '''
    Test that event headers yield add_item and remove_item blocks with class text.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # Both event classes are captured under their comment names.
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    assert [block['name'] for block in blocks] == ['add_item', 'remove_item']
    assert 'class AddItem' in blocks[0]['text']
    assert 'class RemoveItem' in blocks[1]['text']

# ** test: extract_artifact_blocks_none_matching
def test_extract_artifact_blocks_none_matching(sample_lines: List[str]) -> None:
    '''
    Test that a group type with no headers returns an empty list.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # The sample has events, not models.
    assert ArtifactBlockParser.extract_artifact_blocks(
        sample_lines,
        group_type='model',
    ) == []

# ** test: extract_artifact_blocks_line_boundaries
def test_extract_artifact_blocks_line_boundaries(sample_lines: List[str]) -> None:
    '''
    Test that artifact spans start on comment lines and the last ends at EOF.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # The first block closes at the next header; the last closes at EOF.
    add_index = next(
        i for i, line in enumerate(sample_lines) if '# ** event: add_item' in line
    )
    remove_index = next(
        i for i, line in enumerate(sample_lines) if '# ** event: remove_item' in line
    )
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    assert blocks[0]['line_start'] == add_index
    assert blocks[0]['line_end'] == remove_index
    assert blocks[1]['line_start'] == remove_index
    assert blocks[1]['line_end'] == len(sample_lines)

# ** test: extract_artifact_blocks_length_chars
def test_extract_artifact_blocks_length_chars(sample_lines: List[str]) -> None:
    '''
    Test that each artifact block records length_chars as len(text).

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # Character length matches the joined span.
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    assert blocks
    for block in blocks:
        assert block['length_chars'] == len(block['text'])

# ** test: filter_blocks_no_filter
def test_filter_blocks_no_filter(sample_lines: List[str]) -> None:
    '''
    Test that a missing extract set returns every block.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # None means no filter.
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    assert ArtifactBlockParser.filter_blocks(blocks, extract_ids=None) == blocks

# ** test: filter_blocks_with_filter
def test_filter_blocks_with_filter(sample_lines: List[str]) -> None:
    '''
    Test that a name set keeps the matching subset in original order.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # Order follows the source, not the set.
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    filtered = ArtifactBlockParser.filter_blocks(
        blocks,
        extract_ids={'remove_item', 'add_item'},
    )
    assert [block['name'] for block in filtered] == ['add_item', 'remove_item']

# ** test: filter_blocks_no_match
def test_filter_blocks_no_match(sample_lines: List[str]) -> None:
    '''
    Test that a name set with no overlap returns an empty list.

    :param sample_lines: Source lines with an imports section and events.
    :type sample_lines: List[str]
    '''

    # An unknown name drops every block.
    blocks = ArtifactBlockParser.extract_artifact_blocks(sample_lines)
    assert ArtifactBlockParser.filter_blocks(
        blocks,
        extract_ids={'missing'},
    ) == []
