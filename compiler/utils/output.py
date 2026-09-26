"""Scan Output Writer Utility"""

# *** imports

# ** core
import os
import json
from typing import Dict, Any, List, Optional

# ** infra
import yaml

# *** utils

# ** util: scan_output_writer
class ScanOutputWriter:
    '''
    Persist scan and parse result payloads as YAML or JSON.

    Callers name an explicit format or let the output path decide, and split a comma-separated extract-name filter without owning serialization.
    '''

    # * method: detect_format (static)
    @staticmethod
    def detect_format(output_path: str, output_format: str = 'auto') -> str:
        '''
        Resolve the serialization format for an output path.

        :param output_path: Path whose extension is inspected when the format is auto.
        :type output_path: str
        :param output_format: Explicit format, or ``auto`` to detect from the path.
        :type output_format: str
        :return: ``json`` for a ``.json`` path under auto; ``yaml`` for every other auto path; otherwise the given format.
        :rtype: str
        '''

        # Honor an explicit format without inspecting the path.
        if output_format != 'auto':
            return output_format

        # Map .json to json; every other extension, including unknown ones, to yaml.
        ext = os.path.splitext(output_path)[1].lower()
        if ext == '.json':
            return 'json'

        # Unknown extensions do not raise.
        return 'yaml'

    # * method: write (static)
    @staticmethod
    def write(result: Dict[str, Any], output_path: str, output_format: str = 'auto') -> None:
        '''
        Write a result payload to YAML or JSON.

        :param result: The scan or parse result payload.
        :type result: Dict[str, Any]
        :param output_path: Destination file path.
        :type output_path: str
        :param output_format: Explicit format, or ``auto`` to detect from the path.
        :type output_format: str
        :rtype: None
        '''

        # Resolve json versus yaml before opening the file.
        fmt = ScanOutputWriter.detect_format(
            output_path,
            output_format=output_format,
        )

        # Emit JSON with stable indentation, or YAML that preserves key order and anchors.
        with open(output_path, 'w', encoding='utf-8') as output_file:
            if fmt == 'json':
                json.dump(result, output_file, indent=2, default=str)
            else:
                yaml.dump(
                    result,
                    output_file,
                    default_flow_style=False,
                    sort_keys=False,
                )

    # * method: parse_extract_names (static)
    @staticmethod
    def parse_extract_names(extract: str) -> Optional[List[str]]:
        '''
        Parse a comma-separated extract-name filter.

        :param extract: Comma-separated names, or a falsy value for no filter.
        :type extract: str
        :return: ``None`` when extract is falsy; otherwise a stripped, order-preserving list.
        :rtype: Optional[List[str]]
        '''

        # No filter when the caller omits extract names.
        if not extract:
            return None

        # Preserve order and strip surrounding whitespace from each name.
        return [name.strip() for name in extract.split(',')]
