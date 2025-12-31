from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity_services.base.service import BaseService, ServiceType


class ICarConnectivity:
    def get_service_for(self, service_type: ServiceType) -> Optional[BaseService]:
        raise NotImplementedError("Method get_service_for() must be implemented by CarConnectivity")
