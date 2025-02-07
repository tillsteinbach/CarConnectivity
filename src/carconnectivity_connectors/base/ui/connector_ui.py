""" This module contains the base class for connector UI components. """
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Union, Literal, Optional

    import flask

    from carconnectivity_connectors.base.connector import BaseConnector


class BaseConnectorUI:
    """
    A base class for connector UI components.
    """
    def __init__(self, connector: BaseConnector):
        self.blueprint: Optional[flask.Blueprint] = None
        self.connector: BaseConnector = connector

    def get_nav_items(self) -> List[Dict[Literal['text', 'url', 'sublinks', 'divider'], Union[str, List]]]:
        """
        Retrieve navigation items for the UI.

        This method should be implemented by subclasses to provide the navigation
        items required for the user interface. The navigation items are represented
        as a list of dictionaries, where each dictionary contains the following keys:
        - 'text': A string representing the display text of the navigation item.
        - 'url': A string representing the URL the navigation item points to.
        - 'sublinks': A list of sub-navigation items, each following the same structure.
        - 'divider': A string indicating a divider in the navigation menu.
        """
        raise NotImplementedError("Subclasses must provide get_nav_items method")

    def get_title(self) -> str:
        """
        Retrieve the title for the connector UI.

        This method must be implemented by subclasses to provide a specific title.
        """
        raise NotImplementedError("Subclasses must provide get_title method")
