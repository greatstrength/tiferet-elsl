"""Compiler Provision Mappers"""

# *** imports

# ** app
from ..domain.provision import (
    PROVISION_KIND_PRODUCTION,
    PROVISION_KIND_REWRITE,
    PROVISION_KIND_SPECIFICATION,
    Production,
    ProvisionRegistration,
    Rewrite,
    Specification,
)

# *** functions

# ** function: provision_registration_from_row
def provision_registration_from_row(key: str, body: dict) -> ProvisionRegistration:
    '''
    Validate one overlay row, reinjecting the mapping key as its id.

    The key wins when the body also carries ``id``. The asset value omits
    ``id`` the same way, so a later reader still uses ``registration.id``.

    :param key: The provisions mapping key.
    :type key: str
    :param body: The row body, without a trusted id.
    :type body: dict
    :return: The validated registration.
    :rtype: ProvisionRegistration
    '''

    # Spread the body first so the mapping key overwrites a body id.
    return ProvisionRegistration.model_validate({**body, 'id': key})

# ** function: provision_kind_class
def provision_kind_class(kind: str):
    '''
    Return the behavior class for a known provision kind.

    Any other string is not a kind. The caller treats that as a mismatch
    and does not import a module.

    :param kind: The registration kind.
    :type kind: str
    :return: The kind class, or None.
    :rtype: type | None
    '''

    # The three kind strings name the RFP-003 classes and nothing else.
    if kind == PROVISION_KIND_SPECIFICATION:
        return Specification
    if kind == PROVISION_KIND_PRODUCTION:
        return Production
    if kind == PROVISION_KIND_REWRITE:
        return Rewrite
    return None
