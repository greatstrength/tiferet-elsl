"""Tiferet Compiler Type Check Mapper Objects"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** app
from ..domain.typecheck import TypeCheckError

# *** mappers

# ** mapper: type_error_collection
class TypeErrorCollection:
    '''
    Accumulates conformance findings so a checker can report every violation.

    It is an in-memory collector, not a domain object. Callers record each
    finding as the walk proceeds, then take one flat list.
    '''

    # * attribute: errors
    errors: List[TypeCheckError]

    # * init
    def __init__(self) -> None:
        '''
        Initialize an empty finding list.

        :return: None
        :rtype: None
        '''

        # Start with no findings recorded.
        self.errors = []

    # * method: add
    def add(self, error_code: str, message: str, scope_path: str,
            node: Optional[Any] = None, **kwargs) -> None:
        '''
        Record one finding, lifting line and column from the node when present.

        Remaining keys are stored as context and flattened by ``to_list``.

        :param error_code: The finding classification code.
        :type error_code: str
        :param message: The human-readable description.
        :type message: str
        :param scope_path: The scope where the finding was detected.
        :type scope_path: str
        :param node: The optional AST node that carries a source span.
        :type node: Optional[Any]
        :param kwargs: Extra finding keys, excluding the node.
        :type kwargs: dict
        :return: None
        :rtype: None
        '''

        # A missing node has no source span to lift.
        lineno = None
        col = None
        if node is not None:
            lineno = getattr(node, 'lineno', None)
            col = getattr(node, 'col', None)

        # Store the finding. Context keys stay out of the node slot.
        self.errors.append(TypeCheckError(
            error_code=error_code,
            message=message,
            scope_path=scope_path,
            lineno=lineno,
            col=col,
            context=dict(kwargs),
        ))

    # * method: reset
    def reset(self) -> None:
        '''
        Clear recorded findings.

        :return: None
        :rtype: None
        '''

        # Drop the list so the collector can be reused.
        self.errors = []

    # * method: to_list
    def to_list(self) -> List[Dict[str, Any]]:
        '''
        Flatten recorded findings into dicts.

        Each dict has ``error_code``, ``message``, and ``scope_path``.
        ``lineno`` and ``col`` are included only when known. Context keys
        are copied onto the dict.

        :return: The flattened findings, in record order.
        :rtype: List[Dict[str, Any]]
        '''

        # Flatten each stored finding without nesting the context dict.
        rows = []
        for error in self.errors:
            row = {
                'error_code': error.error_code,
                'message': error.message,
                'scope_path': error.scope_path,
            }
            if error.lineno is not None:
                row['lineno'] = error.lineno
            if error.col is not None:
                row['col'] = error.col
            row.update(error.context)
            rows.append(row)

        # Return the flattened rows.
        return rows
