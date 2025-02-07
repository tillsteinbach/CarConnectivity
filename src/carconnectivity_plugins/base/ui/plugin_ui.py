""" Base class for plugin user interfaces. """
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Union, Literal, Optional

    import flask

    from carconnectivity_plugins.base.plugin import BasePlugin


class BasePluginUI:
    """
    Base class for plugin user interfaces.

    This class provides a blueprint for creating user interfaces for plugins. It defines
    the basic structure and methods that must be implemented by subclasses to provide
    specific navigation items and titles for the user interface.
    """
    def __init__(self, plugin: BasePlugin):
        self.blueprint: Optional[flask.Blueprint] = None
        self.plugin: BasePlugin = plugin

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
