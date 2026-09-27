"""Interfaces – Compiler Service ABC Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest
from tiferet import Service

# ** app
from .. import (
    CodegenService,
    LexerService,
    OptimizerService,
    ParserService,
)

# *** tests

# ** test: services_subclass_service
def test_services_subclass_service() -> None:
    '''
    Test that each compiler service subclasses Service.
    '''

    # Each vertical contract extends the unified Service base.
    for service in (
        LexerService,
        ParserService,
        CodegenService,
        OptimizerService,
    ):
        assert issubclass(service, Service)

# ** test: services_are_abstract
def test_services_are_abstract() -> None:
    '''
    Test that each compiler service is abstract and cannot be instantiated.
    '''

    # Instantiation is refused, and each class remains abstract.
    for service in (
        LexerService,
        ParserService,
        CodegenService,
        OptimizerService,
    ):
        with pytest.raises(TypeError):
            service()
        assert inspect.isabstract(service) is True

# ** test: lexer_service_tokenize_is_abstract
def test_lexer_service_tokenize_is_abstract() -> None:
    '''
    Test that LexerService.tokenize is abstract.
    '''

    # tokenize is part of the unimplemented contract.
    assert 'tokenize' in LexerService.__abstractmethods__

# ** test: parser_service_parse_is_abstract
def test_parser_service_parse_is_abstract() -> None:
    '''
    Test that ParserService.parse is abstract.
    '''

    # parse is part of the unimplemented contract.
    assert 'parse' in ParserService.__abstractmethods__

# ** test: codegen_service_generate_is_abstract
def test_codegen_service_generate_is_abstract() -> None:
    '''
    Test that CodegenService.generate is abstract.
    '''

    # generate is part of the unimplemented contract.
    assert 'generate' in CodegenService.__abstractmethods__

# ** test: optimizer_service_optimize_is_abstract
def test_optimizer_service_optimize_is_abstract() -> None:
    '''
    Test that OptimizerService.optimize is abstract.
    '''

    # optimize is part of the unimplemented contract.
    assert 'optimize' in OptimizerService.__abstractmethods__
