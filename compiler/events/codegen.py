"""Code Generation Domain Events"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** infra
from tiferet.utils import Json

# ** app
from ..interfaces.codegen import CodegenService
from ..interfaces.optimizer import OptimizerService
from ..mappers import Decl, DeclarationTransferObject
from ..utils import ScanOutputWriter
from .settings import DomainEvent, a

# *** events

# ** event: generate_code
class GenerateCode(DomainEvent):
    '''
    Turn a module AST into the codegen dict a later pass can emit or optimize.

    The event delegates to the injected code generator. It does not walk the AST.
    '''

    # * attribute: codegen_service
    codegen_service: CodegenService

    # * init
    def __init__(self, codegen_service: CodegenService) -> None:
        '''
        Initialize the code generation event with its generator.

        :param codegen_service: The service that generates a codegen dict.
        :type codegen_service: CodegenService
        '''

        # Store the generator. The event does not construct it.
        self.codegen_service = codegen_service

    # * method: execute
    @DomainEvent.parameters_required(['ast'])
    def execute(self,
            ast: Decl,
            component: str = 'events',
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Generate a codegen dict for a component kind.

        :param ast: The module declaration to generate from.
        :type ast: Decl
        :param component: Requested component type. Passed as the generator kind.
        :type component: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The schema-conforming codegen dict.
        :rtype: Dict[str, Any]
        '''

        # Delegate generation. Do not inspect the AST.
        return self.codegen_service.generate(
            ast,
            kind=component,
        )

# ** event: optimize_code
class OptimizeCode(DomainEvent):
    '''
    Apply an optimization level to a codegen dict.

    O0 leaves the dict unchanged. O1 and above delegate to the injected optimizer.
    '''

    # * attribute: optimizer_service
    optimizer_service: OptimizerService

    # * init
    def __init__(self, optimizer_service: OptimizerService) -> None:
        '''
        Initialize the optimize event with its optimizer.

        :param optimizer_service: The service that shares repeated codegen structures.
        :type optimizer_service: OptimizerService
        '''

        # Store the optimizer. The event does not construct it.
        self.optimizer_service = optimizer_service

    # * method: execute
    @DomainEvent.parameters_required(['codegen'])
    def execute(self,
            codegen: Dict[str, Any],
            O: str = 'O0',
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Optimize a codegen dict when the requested level is O1 or above.

        :param codegen: The codegen dict from generation.
        :type codegen: Dict[str, Any]
        :param O: Optimization level from the CLI ``-O`` flag. Defaults to O0.
        :type O: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The unchanged dict at O0, otherwise the optimized dict.
        :rtype: Dict[str, Any]
        '''

        # Normalize a blank request to O0.
        level = O.strip().upper() if O else 'O0'

        # O0 leaves the dict unchanged and does not call the optimizer.
        if level == 'O0':
            return codegen

        # O1 and above share repeated structures through the optimizer.
        if level >= 'O1':
            codegen = self.optimizer_service.optimize(codegen)

        # Return the possibly optimized dict.
        return codegen

# ** event: emit_codegen_result
class EmitCodegenResult(DomainEvent):
    '''
    Keep a codegen dict or persist it for a later reader.

    A file write replaces the returned payload with an empty string.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['codegen'])
    def execute(self,
            codegen: Dict[str, Any],
            source_file: str = None,
            output_format: str = 'auto',
            output: str = None,
            **kwargs,
        ) -> Any:
        '''
        Return a codegen dict, or write it when a destination path is set.

        :param codegen: The codegen dict to keep or persist.
        :type codegen: Dict[str, Any]
        :param source_file: Accepted for the emitter. Unused by this event.
        :type source_file: str
        :param output_format: Serialization format. Defaults to auto.
        :type output_format: str
        :param output: Optional destination path. When set, the write replaces the return value.
        :type output: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The codegen dict, or an empty string after a file write.
        :rtype: Any
        '''

        # The caller may pass source_file. This event does not use it.
        del source_file

        # Write the dict and return an empty string when a path is set.
        if output:
            ScanOutputWriter.write(
                codegen,
                output,
                output_format=output_format,
            )
            return ''

        # Otherwise return the dict.
        return codegen

# ** event: load_from_ast
class LoadFromAST(DomainEvent):
    '''
    Rebuild a module declaration from a JSON AST so generation can start from a saved parse.

    The event loads the file and maps the transfer object. It does not parse source.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['source_file'])
    def execute(self,
            source_file: str,
            **kwargs,
        ) -> Decl:
        '''
        Load a JSON AST and map it back to a module declaration.

        :param source_file: Path of the UTF-8 JSON AST file.
        :type source_file: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The mapped module declaration.
        :rtype: Decl
        '''

        # Load the JSON file. A missing file surfaces from the file layer.
        data = Json(
            source_file,
            encoding='utf-8',
        ).load()

        # Accept a parse-result payload or a bare AST dict.
        ast_dict = data.get('ast', data)

        # Map the transfer object back to a declaration. Do not walk the AST.
        return DeclarationTransferObject.model_validate(ast_dict).map()
