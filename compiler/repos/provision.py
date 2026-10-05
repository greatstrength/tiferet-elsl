"""Compiler Provision Configuration Repository"""

# *** imports

# ** infra
from tiferet.repos.core import ConfigurationRepository

# ** app
from ..mappers.provision import provision_registration_from_row

# *** constants

# ** constant: provision_config_section
PROVISION_CONFIG_SECTION = 'provisions'

# *** repos

# ** repo: provision_config_repository
class ProvisionConfigRepository(ConfigurationRepository):
    '''
    Read a consumer provisions section without constructing behavior.

    The repository returns validated registrations and ignores every other
    top-level key. It does not walk a tree and it does not write a cache.
    '''

    # * init
    def __init__(self, provision_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the provision configuration repository.

        :param provision_config: Path to the configuration file.
        :type provision_config: str
        :param encoding: File encoding.
        :type encoding: str
        :return: None
        :rtype: None
        '''

        # Forward the path as the configuration file. Do not load it yet.
        ConfigurationRepository.__init__(
            self,
            config_file=provision_config,
            encoding=encoding,
        )

    # * method: list
    def list(self) -> list:
        '''
        Return the provision registrations in file order.

        A missing or null section is no rows. The mapping key is reinjected
        as ``id`` and wins over a body ``id``.

        :return: Validated provision registrations.
        :rtype: list
        '''

        # Load only the provisions section. A missing key is an empty mapping.
        section = self._load(
            start_node=lambda data: data.get(PROVISION_CONFIG_SECTION, {}),
        )

        # A present null is no rows, not an error.
        if section is None:
            return []

        # A list or other non-mapping is not a provision section.
        if not isinstance(section, dict):
            raise TypeError(
                f"Provision section '{PROVISION_CONFIG_SECTION}' must be a mapping.",
            )

        # Validate each row. A non-dict value is not a registration body.
        registrations = []
        for key, body in section.items():
            if not isinstance(body, dict):
                raise TypeError(
                    f"Provision '{key}' must be a mapping.",
                )
            registrations.append(provision_registration_from_row(key, body))

        # Return the registrations in file order. Do not instantiate them.
        return registrations
