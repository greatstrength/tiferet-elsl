"""Tiferet Compiler Code Generation Mapper Objects"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** infra
from pydantic import Field, PrivateAttr
from tiferet.mappers import Aggregate

# ** app
from ..domain.codegen import (
    EventData,
    ImportEntry,
    SnippetData,
)

# *** mappers

# ** mapper: import_entry_collector
class ImportEntryCollector(Aggregate):
    '''
    Collapses same-module imports into one ordered entry per module path.

    Distillation records imports as ``{src, tgts}`` lines. First-seen module
    order is the document order; later symbols append to that entry.
    '''

    # * attribute: entries
    entries: List[ImportEntry] = Field(
        default_factory=list,
        description='Ordered import entries, one per first-seen module path.',
    )

    # * attribute: _index
    _index: Dict[str, int] = PrivateAttr(
        default_factory=dict,
    )

    # * method: add
    def add(self, module_path: str, symbol: str) -> None:
        '''
        Record a symbol under its module path.

        A module path already seen appends ``symbol`` to that entry.
        Otherwise a new entry is appended, preserving first-seen order.

        :param module_path: The module the symbol is imported from.
        :type module_path: str
        :param symbol: The imported symbol name.
        :type symbol: str
        :return: None
        :rtype: None
        '''

        # Append to the existing entry when this module was seen before.
        if module_path in self._index:
            self.entries[self._index[module_path]].tgts.append(symbol)
            return

        # Record the first-seen index, then append a new entry.
        self._index[module_path] = len(self.entries)
        self.entries.append(ImportEntry(
            src=module_path,
            tgts=[symbol],
        ))

    # * method: to_list
    def to_list(self) -> List[Dict[str, Any]]:
        '''
        Serialize entries as ``{src, tgts}`` dicts in first-seen order.

        :return: The ordered import rows.
        :rtype: List[Dict[str, Any]]
        '''

        # Project each stored entry. Do not re-sort.
        return [
            {
                'src': entry.src,
                'tgts': list(entry.tgts),
            }
            for entry in self.entries
        ]


# ** mapper: snippet_accumulator
class SnippetAccumulator(SnippetData, Aggregate):
    '''
    Accumulates a snippet body and serializes it under codegen keys.

    Domain fields stay ``comments`` and ``statements``. The ``coms`` /
    ``stmt`` rename happens only when the snippet is serialized.
    '''

    # * method: add_comment
    def add_comment(self, text: str) -> None:
        '''
        Append a leading comment line.

        The caller strips the leading hash and trims the text.

        :param text: The comment text to store.
        :type text: str
        :return: None
        :rtype: None
        '''

        # Store the caller-prepared comment text.
        self.comments.append(text)

    # * method: add_statement
    def add_statement(self, expr_str: str) -> None:
        '''
        Append an encoded statement when it is non-blank.

        :param expr_str: The encoded statement text.
        :type expr_str: str
        :return: None
        :rtype: None
        '''

        # Blank and whitespace-only statements are not a snippet body.
        if expr_str and expr_str.strip():
            self.statements.append(expr_str)

    # * method: to_dict
    def to_dict(self) -> Optional[Dict[str, Any]]:
        '''
        Serialize comments and statements under ``coms`` and ``stmt``.

        :return: The snippet dict, or None when both lists are empty.
        :rtype: Optional[Dict[str, Any]]
        '''

        # Rename only the lists that have content.
        data = {}
        if self.comments:
            data['coms'] = list(self.comments)
        if self.statements:
            data['stmt'] = list(self.statements)

        # An empty snippet is absence, not an empty dict.
        return data or None


# ** mapper: event_accumulator
class EventAccumulator(EventData, Aggregate):
    '''
    Accumulates a class payload and serializes only the filled sections.

    Envelope keys such as ``base`` and ``kind`` belong to the generator.
    ``execute`` is omitted until a truthy codegen payload is set.
    '''

    # * attribute: execute
    execute: Optional[Dict[str, Any]] = Field(
        default=None,
        description='Codegen execute payload. Included only when truthy.',
    )

    # * method: add_attribute
    def add_attribute(self, name: str, type_name: str,
                      init: Optional[str] = None) -> None:
        '''
        Append an attribute member.

        Without ``init`` the entry is ``{name: type_name}``. With a truthy
        ``init`` it is ``{name: {type, init}}``.

        :param name: The attribute name.
        :type name: str
        :param type_name: The attribute type name.
        :type type_name: str
        :param init: The optional encoded initializer.
        :type init: Optional[str]
        :return: None
        :rtype: None
        '''

        # A truthy initializer nests type and init; otherwise store the type.
        if init:
            self.attributes.append({
                name: {
                    'type': type_name,
                    'init': init,
                },
            })
            return

        # No initializer: the value is the type name alone.
        self.attributes.append({name: type_name})

    # * method: add_injection
    def add_injection(self, spec: str, value: Dict[str, Any]) -> None:
        '''
        Append a constructor injection entry.

        ``spec`` has the shape ``name:type:required::desc``.

        :param spec: The colon-delimited injection spec.
        :type spec: str
        :param value: The injection value, typically an assign payload.
        :type value: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # One spec maps to one value. Do not merge specs.
        self.injections.append({spec: value})

    # * method: set_execute
    def set_execute(self, data: Dict[str, Any]) -> None:
        '''
        Store the codegen execute payload.

        A falsy payload is stored and later omitted by ``to_dict``.

        :param data: The execute payload dict.
        :type data: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Keep the dict as given so serialization can echo it.
        self.execute = data

    # * method: add_method
    def add_method(self, name: str, data: Dict[str, Any]) -> None:
        '''
        Store a non-execute method payload under its name.

        :param name: The method name.
        :type name: str
        :param data: The method payload.
        :type data: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Key the payload by method name. Later adds replace that name.
        self.methods[name] = data

    # * method: to_dict
    def to_dict(self) -> Dict[str, Any]:
        '''
        Serialize the class payload, omitting empty optional sections.

        ``name`` is always included. ``desc``, ``attributes``,
        ``injections``, ``execute``, and ``methods`` are included only when
        set. ``base``, ``maps``, ``kind``, ``implements``, and
        ``collaborators`` are left for the generator.

        :return: The serialized class payload.
        :rtype: Dict[str, Any]
        '''

        # Name is the only required key.
        payload = {
            'name': self.name,
        }

        # Omit empty optional sections rather than emitting empty containers.
        if self.desc:
            payload['desc'] = self.desc
        if self.attributes:
            payload['attributes'] = list(self.attributes)
        if self.injections:
            payload['injections'] = list(self.injections)
        if self.execute:
            payload['execute'] = self.execute
        if self.methods:
            payload['methods'] = dict(self.methods)

        # Return the filled sections only.
        return payload
