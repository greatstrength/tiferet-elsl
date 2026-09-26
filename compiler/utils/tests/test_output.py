"""Scan Output Writer Utility Tests"""

# *** imports

# ** core
import json

# ** infra
import yaml

# ** app
from ..output import ScanOutputWriter

# *** constants

# ** constant: sample_payload
SAMPLE_PAYLOAD = {
    'event_type': 'TokensScanned',
    'token_count': 5,
}

# *** tests

# ** test: detect_format_auto_json
def test_detect_format_auto_json() -> None:
    '''
    Test that auto detection maps a .json path to json.
    '''

    # A .json extension under auto resolves to json.
    assert ScanOutputWriter.detect_format('output.json', output_format='auto') == 'json'

# ** test: detect_format_auto_yaml
def test_detect_format_auto_yaml() -> None:
    '''
    Test that auto detection maps a .yaml path to yaml.
    '''

    # A .yaml extension under auto resolves to yaml.
    assert ScanOutputWriter.detect_format('output.yaml', output_format='auto') == 'yaml'

# ** test: detect_format_auto_unknown_defaults_yaml
def test_detect_format_auto_unknown_defaults_yaml() -> None:
    '''
    Test that an unknown extension under auto resolves to yaml without raising.
    '''

    # Unknown extensions do not raise; they default to yaml.
    assert ScanOutputWriter.detect_format('output.txt', output_format='auto') == 'yaml'

# ** test: detect_format_explicit
def test_detect_format_explicit() -> None:
    '''
    Test that an explicit format is returned unchanged.
    '''

    # An explicit format wins over the path extension.
    assert ScanOutputWriter.detect_format('output.yaml', output_format='json') == 'json'

# ** test: write_yaml
def test_write_yaml(tmp_path) -> None:
    '''
    Test that write emits valid YAML containing the payload keys.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Write the sample payload as YAML.
    output_path = tmp_path / 'output.yaml'
    ScanOutputWriter.write(
        SAMPLE_PAYLOAD,
        str(output_path),
        output_format='yaml',
    )

    # The file is valid YAML with the expected keys.
    loaded = yaml.safe_load(output_path.read_text(encoding='utf-8'))
    assert loaded['event_type'] == 'TokensScanned'
    assert loaded['token_count'] == 5

# ** test: write_json
def test_write_json(tmp_path) -> None:
    '''
    Test that write emits valid JSON containing the payload keys.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Write the sample payload as JSON.
    output_path = tmp_path / 'output.json'
    ScanOutputWriter.write(
        SAMPLE_PAYLOAD,
        str(output_path),
        output_format='json',
    )

    # The file is valid JSON with the expected keys.
    loaded = json.loads(output_path.read_text(encoding='utf-8'))
    assert loaded['event_type'] == 'TokensScanned'
    assert loaded['token_count'] == 5

# ** test: write_auto_json
def test_write_auto_json(tmp_path) -> None:
    '''
    Test that auto format on a .json path writes JSON.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Auto-detect format from the .json path.
    output_path = tmp_path / 'output.json'
    ScanOutputWriter.write(
        SAMPLE_PAYLOAD,
        str(output_path),
        output_format='auto',
    )

    # The file is valid JSON, not YAML.
    loaded = json.loads(output_path.read_text(encoding='utf-8'))
    assert loaded['event_type'] == 'TokensScanned'
    assert loaded['token_count'] == 5

# ** test: parse_extract_names_none
def test_parse_extract_names_none() -> None:
    '''
    Test that a missing extract filter returns None.
    '''

    # Falsy None means no extract filter.
    assert ScanOutputWriter.parse_extract_names(None) is None

# ** test: parse_extract_names_empty
def test_parse_extract_names_empty() -> None:
    '''
    Test that an empty extract filter returns None.
    '''

    # An empty string means no extract filter.
    assert ScanOutputWriter.parse_extract_names('') is None

# ** test: parse_extract_names_single
def test_parse_extract_names_single() -> None:
    '''
    Test that a single extract name is returned as a one-item list.
    '''

    # A single name is preserved as a list.
    assert ScanOutputWriter.parse_extract_names('add_item') == ['add_item']

# ** test: parse_extract_names_multiple
def test_parse_extract_names_multiple() -> None:
    '''
    Test that comma-separated extract names are stripped and order-preserving.
    '''

    # Whitespace around names is stripped; order is preserved.
    assert ScanOutputWriter.parse_extract_names(
        'add_item, remove_item , get_item',
    ) == ['add_item', 'remove_item', 'get_item']

# ** test: anchored_yaml_output
def test_anchored_yaml_output(tmp_path) -> None:
    '''
    Test that a shared list is written with YAML anchors and round-trips.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Two events share one list object so the dumper can emit an anchor.
    shared = ['a:int:true::', 'b:int:true::']
    payload = {
        'events': [
            {'parameters': shared},
            {'parameters': shared},
        ],
    }
    output_path = tmp_path / 'anchored.yaml'
    ScanOutputWriter.write(
        payload,
        str(output_path),
        output_format='yaml',
    )

    # Anchors and aliases are present, and the list round-trips.
    text = output_path.read_text(encoding='utf-8')
    assert '&' in text
    assert '*' in text
    loaded = yaml.safe_load(text)
    assert loaded['events'][0]['parameters'] == ['a:int:true::', 'b:int:true::']
    assert loaded['events'][1]['parameters'] == ['a:int:true::', 'b:int:true::']
