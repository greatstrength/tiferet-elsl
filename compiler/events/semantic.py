"""Semantic Analysis Domain Events"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import List, Dict, Any

# ** app
from ..mappers import Decl
from ..utils import ScanOutputWriter, SymbolTableBuilder, NameResolver
from .settings import DomainEvent, a

# *** events

# ** event: perform_semantic_analysis
class PerformSemanticAnalysis(DomainEvent):
    '''
    Turn a parsed module AST into the symbol table and name resolution a later pass can consume.

    The event runs the symbol-table builder, then the name resolver. It does not
    own scope construction, and it does not print findings.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['ast'])
    def execute(self,
            ast: Decl,
            source_file: str = None,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Build a symbol table and resolve names in a module AST.

        :param ast: The parsed module declaration.
        :type ast: Decl
        :param source_file: Accepted for the emitter. Unused by this event.
        :type source_file: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The symbol table and dumped resolution.
        :rtype: Dict[str, Any]
        '''

        # The emitter consumes source_file. This event only needs the AST.
        del source_file

        # Reject a missing or non-declaration AST.
        self.verify(
            expression=ast and isinstance(ast, Decl),
            error_code='INVALID_AST_STRUCTURE',
            message='Semantic analysis requires a valid Module AST',
            ast_type=str(type(ast)),
        )

        # Build the symbol table, then resolve names against the live scopes.
        builder = SymbolTableBuilder()
        symbol_table = builder.build(ast)
        resolver = NameResolver(builder.scopes)
        resolution = resolver.resolve(ast)

        # Return dumped scopes and the resolution dump.
        return {
            'symbol_table': symbol_table,
            'resolution': resolution.model_dump(exclude_none=True),
        }

# ** event: emit_semantic_result
class EmitSemanticResult(DomainEvent):
    '''
    Record that semantic analysis finished so a caller can keep or persist the result.

    When conformance findings are present, the payload omits symbol-table data
    and prints each finding. A file write replaces the returned payload with an empty string.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['semantic'])
    def execute(self,
            semantic: Dict[str, Any],
            findings: List[Dict] = None,
            ast: Decl = None,
            source_file: str = None,
            include_ast: bool = False,
            output_format: str = 'auto',
            output: str = None,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Build a SemanticAnalysisCompleted payload and optionally write it.

        :param semantic: The symbol table and resolution from analysis.
        :type semantic: Dict[str, Any]
        :param findings: Conformance findings. Non-empty findings omit symbol-table data.
        :type findings: List[Dict]
        :param ast: Optional module declaration included only when requested.
        :type ast: Decl
        :param source_file: Path of the analyzed source file.
        :type source_file: str
        :param include_ast: Whether to add the dumped AST.
        :type include_ast: bool
        :param output_format: Serialization format. Defaults to auto.
        :type output_format: str
        :param output: Optional destination path. When set, the write replaces the return value.
        :type output: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The SemanticAnalysisCompleted payload, or an empty string after a file write.
        :rtype: Dict[str, Any]
        '''

        # Print each finding when the list is non-empty. Do not pretty-print the AST.
        if isinstance(findings, list) and findings:
            for finding in findings:
                error_code = finding.get('error_code') or 'UNKNOWN'
                scope_path = finding.get('scope_path') or '?'
                message = finding.get('message') or ''
                lineno = finding.get('lineno')
                loc = ''
                if lineno is not None:
                    col = finding.get('col')
                    if col is None:
                        col = '?'
                    loc = f' (line {lineno}, col {col})'
                print(f'Type Error [{error_code}] in {scope_path}{loc}: {message}')

        # Always record the completion event, UTC timestamp, and source file.
        result = {
            'event_type': 'SemanticAnalysisCompleted',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_file': source_file,
        }

        # Omit symbol-table data when conformance findings are present.
        if not findings:
            result['symbol_table'] = semantic.get('symbol_table', {})
            result['resolution'] = semantic.get('resolution', {})

        # Include the dumped AST only when requested and the AST is a declaration.
        if include_ast and isinstance(ast, Decl):
            result['ast'] = ast.model_dump(
                exclude_none=True,
                exclude_unset=True,
            )

        # Write the payload and return an empty string when a destination is given.
        if output:
            ScanOutputWriter.write(
                result,
                output,
                output_format=output_format,
            )
            return ''

        # Otherwise return the payload.
        return result
