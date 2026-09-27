"""Optimizer Service Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Dict

# ** infra
from tiferet import Service

# *** interfaces

# ** interface: optimizer_service
class OptimizerService(Service):
    '''
    Abstract interface for optimizing codegen output with YAML anchors and aliases.
    '''

    # * method: optimize
    @abstractmethod
    def optimize(self, codegen: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Share repeated structures in a codegen dict so PyYAML can emit anchors.

        :param codegen: Codegen dict from the generator.
        :type codegen: Dict[str, Any]
        :return: The same dict shape with repeated structures shared so PyYAML can emit anchors.
        :rtype: Dict[str, Any]
        '''

        # Abstract contract; concrete optimizer adapters implement this method.
        raise NotImplementedError()
