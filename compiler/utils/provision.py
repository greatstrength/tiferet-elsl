"""Compiler Provision Instantiation"""

# *** imports

# ** core
import importlib
from typing import Any, Dict, List, Optional, Tuple

# ** app
from ..mappers import ProvisionRegistration
from ..mappers.provision import provision_kind_class

# *** constants

# ** constant: provision_row_invalid
PROVISION_ROW_INVALID = 'PROVISION_ROW_INVALID'

# ** constant: provision_kind_mismatch
PROVISION_KIND_MISMATCH = 'PROVISION_KIND_MISMATCH'

# ** constant: provision_import_failed
PROVISION_IMPORT_FAILED = 'PROVISION_IMPORT_FAILED'

# ** constant: provision_class_mismatch
PROVISION_CLASS_MISMATCH = 'PROVISION_CLASS_MISMATCH'

# ** constant: provision_init_failed
PROVISION_INIT_FAILED = 'PROVISION_INIT_FAILED'

# ** constant: bound_domain_type_predicate
BOUND_DOMAIN_TYPE_PREDICATE = 'compiler.utils.core.declares_bound_domain_type'

# *** functions

# ** function: _provision_id
def _provision_id(value: Any, cache_key: Optional[str] = None) -> str:
    '''
    Return the provision id when the value has one, otherwise the cache key.

    :param value: The cached value.
    :type value: Any
    :param cache_key: The key the value was stored under.
    :type cache_key: Optional[str]
    :return: The id to cite on a finding.
    :rtype: str
    '''

    # A present id wins over the cache key.
    row_id = getattr(value, 'id', None)
    if isinstance(row_id, str) and row_id:
        return row_id

    # Otherwise cite the cache key, or an empty path when neither is known.
    return cache_key or ''

# ** function: _finding
def _finding(error_code: str, message: str, scope_path: str) -> Dict[str, str]:
    '''
    Build one instantiation finding.

    The dict has no lineno, column, or node. Those belong to a walk.

    :param error_code: The finding code.
    :type error_code: str
    :param message: The finding message. It contains the id.
    :type message: str
    :param scope_path: The provision id, or the cache key.
    :type scope_path: str
    :return: The finding dict.
    :rtype: Dict[str, str]
    '''

    # Keep the channel to the three keys the readers prepend.
    return {
        'error_code': error_code,
        'message': message,
        'scope_path': scope_path,
    }

# ** function: _load_bound_domain_predicate
def _load_bound_domain_predicate():
    '''
    Import the one predicate string this boundary resolves.

    A missing attribute or a non-callable is a failed import. The caller
    does not construct the class.

    :return: The predicate function, or None.
    :rtype: Any
    '''

    # Import the named function. Do not resolve any other dotted string.
    try:
        module = importlib.import_module('compiler.utils.core')
        predicate = getattr(module, 'declares_bound_domain_type')
    except Exception:
        return None

    # A present non-callable is still an import failure.
    if not callable(predicate):
        return None
    return predicate

# ** function: instantiate_provision
def instantiate_provision(registration: Any,
        cache_key: str = None) -> Tuple[Any, Optional[Dict[str, str]]]:
    '''
    Construct one provision from a registration, or return a finding.

    Exactly one of the instance and the finding is None. The registration
    is not mutated. ``cache_key`` is used only when the value has no id.

    :param registration: The cached value.
    :type registration: Any
    :param cache_key: The cache key, when the caller has one.
    :type cache_key: str
    :return: The instance and None, or None and a finding.
    :rtype: Tuple[Any, Optional[Dict[str, str]]]
    '''

    # A non-registration is invalid and is not imported.
    scope_path = _provision_id(registration, cache_key)
    if not isinstance(registration, ProvisionRegistration):
        return None, _finding(
            PROVISION_ROW_INVALID,
            f"Provision '{scope_path}' is not a registration.",
            scope_path,
        )

    # An unknown kind does not import the named module.
    kind_cls = provision_kind_class(registration.kind)
    if kind_cls is None:
        return None, _finding(
            PROVISION_KIND_MISMATCH,
            (
                f"Provision '{registration.id}' has kind "
                f"'{registration.kind}', which is not a known kind."
            ),
            registration.id,
        )

    # Import the named class. Any import failure is a finding, not a raise.
    try:
        module = importlib.import_module(registration.module_path)
        cls = getattr(module, registration.class_name)
    except Exception:
        return None, _finding(
            PROVISION_IMPORT_FAILED,
            (
                f"Provision '{registration.id}' could not be imported "
                f"from '{registration.module_path}.{registration.class_name}'."
            ),
            registration.id,
        )

    # The loaded object must be a class and a subclass of the kind, including itself.
    if not isinstance(cls, type) or not issubclass(cls, kind_cls):
        return None, _finding(
            PROVISION_CLASS_MISMATCH,
            (
                f"Provision '{registration.id}' class '{registration.class_name}' "
                f"is not a subclass of {kind_cls.__name__}."
            ),
            registration.id,
        )

    # Copy parameters so the cached registration keeps the catalog string.
    resolved = dict(registration.parameters or {})
    if resolved.get('predicate') == BOUND_DOMAIN_TYPE_PREDICATE:
        predicate = _load_bound_domain_predicate()
        if predicate is None:
            return None, _finding(
                PROVISION_IMPORT_FAILED,
                (
                    f"Provision '{registration.id}' could not import "
                    f"'{BOUND_DOMAIN_TYPE_PREDICATE}'."
                ),
                registration.id,
            )
        resolved['predicate'] = predicate

    # Construct with the registration id, not a body field or the cache key.
    try:
        instance = cls(
            id=registration.id,
            applies_to=registration.applies_to,
            **resolved,
        )
    except Exception:
        return None, _finding(
            PROVISION_INIT_FAILED,
            f"Provision '{registration.id}' could not be constructed.",
            registration.id,
        )

    # One of the pair is None. Success returns the instance.
    return instance, None

# ** function: collect_owned_provisions
def collect_owned_provisions(rows: Dict[str, Any],
        owned_prefix: str,
        kind: str) -> Tuple[List[Any], List[Dict[str, str]]]:
    '''
    Instantiate the rows one reader owns, in cache order.

    A matching prefix with another kind is a mismatch and is not instantiated.
    Any other prefix is left in the cache and is not a finding here.

    :param rows: The provision namespace, in insertion order.
    :type rows: Dict[str, Any]
    :param owned_prefix: The id prefix, including the trailing dot.
    :type owned_prefix: str
    :param kind: The kind this reader attaches.
    :type kind: str
    :return: Successful instances and instantiation findings.
    :rtype: Tuple[List[Any], List[Dict[str, str]]]
    '''

    # Do not sort. Cache order is the order the seed and overlay wrote.
    instances = []
    findings = []
    for key, row in rows.items():
        row_id = _provision_id(row, key)
        if not str(row_id).startswith(owned_prefix):
            continue

        # A wrong kind on an owned id is a finding and is not imported.
        if isinstance(row, ProvisionRegistration) and row.kind != kind:
            findings.append(_finding(
                PROVISION_KIND_MISMATCH,
                (
                    f"Provision '{row_id}' is kind '{row.kind}', not '{kind}'."
                ),
                row_id,
            ))
            continue

        # A matching kind, or a non-registration, goes through instantiation.
        instance, finding = instantiate_provision(row, cache_key=key)
        if finding is not None:
            findings.append(finding)
            continue
        instances.append(instance)

    # Return both lists. The caller does not read the namespace again.
    return instances, findings
