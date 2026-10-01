"""Artifact Block Parser Utility"""

# *** imports

# ** core
import re
from typing import List, Dict, Any, Set, Optional

# *** utils

# ** util: artifact_block_parser
class ArtifactBlockParser:
    '''
    Slice structured Tiferet comments into import, group-header, and named artifact blocks.

    Callers pass source lines and receive index spans, so selection stays independent of the lexer and the parse phase.
    '''

    # * method: parse_extract_filter (static)
    @staticmethod
    def parse_extract_filter(extract: str) -> Optional[Set[str]]:
        '''
        Parse a comma-separated extract-name filter into a set.

        :param extract: Comma-separated names, or a falsy value for no filter.
        :type extract: str
        :return: ``None`` when extract is falsy; otherwise a set of stripped names.
        :rtype: Optional[Set[str]]
        '''

        # No filter when the caller omits extract names.
        if not extract:
            return None

        # Strip surrounding whitespace from each comma-separated name.
        return set(name.strip() for name in extract.split(','))

    # * method: extract_imports_block (static)
    @staticmethod
    def extract_imports_block(lines: List[str]) -> Optional[Dict[str, Any]]:
        '''
        Extract the top-level imports section as one block.

        :param lines: Source lines, typically from ``splitlines(keepends=True)``.
        :type lines: List[str]
        :return: The ``__imports__`` block, or ``None`` when imports is missing or has no following top-level section.
        :rtype: Optional[Dict[str, Any]]
        '''

        # Compile the imports header and the next top-level section marker.
        imports_start_pattern = re.compile(r'^\s*#\s*\*{3}\s+imports\s*$')
        top_level_pattern = re.compile(r'^\s*#\s*\*{3}\s+\S+')

        # Record the imports header, then close the block at the next top-level section.
        imports_start = None
        for i, line in enumerate(lines):
            if imports_start is None:
                if imports_start_pattern.match(line):
                    imports_start = i
                continue

            if top_level_pattern.match(line):
                text = ''.join(lines[imports_start:i])
                return {
                    'name': '__imports__',
                    'line_start': imports_start,
                    'line_end': i,
                    'text': text,
                    'length_chars': len(text),
                }

        # Missing imports, or imports with no following section, is not a block.
        return None

    # * method: extract_group_header (static)
    @staticmethod
    def extract_group_header(lines: List[str]) -> Optional[Dict[str, Any]]:
        '''
        Extract the first non-imports top-level section header.

        :param lines: Source lines, typically from ``splitlines(keepends=True)``.
        :type lines: List[str]
        :return: A one-line ``__group_header__`` block, or ``None`` when no such header exists.
        :rtype: Optional[Dict[str, Any]]
        '''

        # Match a top-level section and capture its name.
        top_level_pattern = re.compile(r'^\s*#\s*\*{3}\s+(\S+)')

        # Use the first header that is not the imports section.
        for i, line in enumerate(lines):
            match = top_level_pattern.match(line)
            if match is None or match.group(1) == 'imports':
                continue

            return {
                'name': '__group_header__',
                'line_start': i,
                'line_end': i + 1,
                'text': line,
                'length_chars': len(line),
            }

        # No construct-group header was found.
        return None

    # * method: extract_artifact_blocks (static)
    @staticmethod
    def extract_artifact_blocks(lines: List[str], group_type: str = 'event') -> List[Dict[str, Any]]:
        '''
        Extract named mid-level artifact blocks for one group type.

        :param lines: Source lines, typically from ``splitlines(keepends=True)``.
        :type lines: List[str]
        :param group_type: Mid-level comment kind, such as ``event``.
        :type group_type: str
        :return: Blocks named from ``# ** <group_type>: <name>``, closed at the next header or EOF.
        :rtype: List[Dict[str, Any]]
        '''

        # Match mid-level headers for the requested group type only.
        pattern = re.compile(
            r'^\s*#\s*\*\*\s+' + re.escape(group_type) + r':\s+(\S+)'
        )

        # Close each open block at the next header, then close the last at EOF.
        blocks = []
        open_name = None
        open_start = None
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if not match:
                continue

            if open_name is not None:
                text = ''.join(lines[open_start:i])
                blocks.append({
                    'name': open_name,
                    'line_start': open_start,
                    'line_end': i,
                    'text': text,
                    'length_chars': len(text),
                })

            open_name = match.group(1)
            open_start = i

        if open_name is not None:
            text = ''.join(lines[open_start:len(lines)])
            blocks.append({
                'name': open_name,
                'line_start': open_start,
                'line_end': len(lines),
                'text': text,
                'length_chars': len(text),
            })

        # Return the list, empty when no header matched.
        return blocks

    # * method: filter_blocks (static)
    @staticmethod
    def filter_blocks(blocks: List[Dict[str, Any]], extract_ids: Optional[Set[str]]) -> List[Dict[str, Any]]:
        '''
        Keep blocks whose names are in the extract set.

        :param blocks: Blocks from an extractor.
        :type blocks: List[Dict[str, Any]]
        :param extract_ids: Names to keep, or a falsy value to keep every block.
        :type extract_ids: Optional[Set[str]]
        :return: The original list when extract_ids is falsy; otherwise the matching subset in original order.
        :rtype: List[Dict[str, Any]]
        '''

        # No filter returns the blocks unchanged.
        if not extract_ids:
            return blocks

        # Preserve order and drop names outside the extract set.
        return [block for block in blocks if block['name'] in extract_ids]
