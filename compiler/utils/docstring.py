"""Docstring Parser Utility"""

# *** imports

# ** core
import re
from typing import Dict, List

# *** utils

# ** util: docstring_parser
class DocstringParser:
    '''
    Extract structured parameter and return descriptions from RST docstrings.

    Strips triple-quote delimiters and maps field markers without invoking
    the lexer or rewriting source.
    '''

    # * method: strip (static)
    @staticmethod
    def strip(raw: str) -> str:
        '''
        Remove surrounding whitespace and triple-quote delimiters from a docstring.

        :param raw: The raw docstring text, including optional delimiters.
        :type raw: str
        :return: The stripped docstring body, or an empty string when raw is falsy.
        :rtype: str
        '''

        # Return an empty string when the raw text is missing.
        if not raw:
            return ''

        # Strip surrounding whitespace before delimiter removal.
        s = raw.strip()

        # Remove a leading triple-quote delimiter when present.
        if s.startswith('"""') or s.startswith("'''"):
            s = s[3:]

        # Remove a trailing triple-quote delimiter when present.
        if s.endswith('"""') or s.endswith("'''"):
            s = s[:-3]

        # Return the remaining body with surrounding whitespace removed.
        return s.strip()

    # * method: parse_param_descriptions (static)
    @staticmethod
    def parse_param_descriptions(raw: str) -> Dict[str, str]:
        '''
        Map RST `:param` names to collapsed-whitespace descriptions.

        :param raw: The raw docstring text.
        :type raw: str
        :return: Parameter names mapped to their descriptions.
        :rtype: Dict[str, str]
        '''

        # Strip delimiters before scanning field markers.
        text = DocstringParser.strip(raw)

        # Collect each :param name and its collapsed description.
        descriptions = {}
        pattern = r':param\s+(\w+):\s*(.+?)(?=\n\s*:|$)'
        for match in re.finditer(pattern, text, re.DOTALL):
            descriptions[match.group(1)] = ' '.join(match.group(2).split())

        # Return the parameter map, empty when none match.
        return descriptions

    # * method: parse_return_descriptions (static)
    @staticmethod
    def parse_return_descriptions(raw: str) -> List[str]:
        '''
        Collect RST `:return` and `:returns` descriptions.

        :param raw: The raw docstring text.
        :type raw: str
        :return: Collapsed return descriptions in document order.
        :rtype: List[str]
        '''

        # Strip delimiters before scanning field markers.
        text = DocstringParser.strip(raw)

        # Collect each :return / :returns description.
        descriptions = []
        pattern = r':returns?:\s*(.+?)(?=\n\s*:|$)'
        for match in re.finditer(pattern, text, re.DOTALL):
            descriptions.append(' '.join(match.group(1).split()))

        # Return the descriptions, empty when none match.
        return descriptions
