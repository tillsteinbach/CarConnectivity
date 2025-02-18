""" Base class for plugin user interfaces. """
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import flask
import flask_login

from carconnectivity.util import config_remove_credentials

if TYPE_CHECKING:
    from typing import List, Dict, Union, Literal

    from carconnectivity_plugins.base.plugin import BasePlugin


class BasePluginUI:
    """
    Base class for plugin user interfaces.

    This class provides a blueprint for creating user interfaces for plugins. It defines
    the basic structure and methods that must be implemented by subclasses to provide
    specific navigation items and titles for the user interface.
    """
    def __init__(self, plugin: BasePlugin, blueprint: flask.Blueprint):
        self.blueprint: flask.Blueprint = blueprint
        self.plugin: BasePlugin = plugin

        @self.blueprint.route('/log', methods=['GET'])
        @flask_login.login_required
        def log():
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            return flask.render_template('plugins/log.html', current_app=flask.current_app, plugin=self.plugin, formatter=formatter)

        @self.blueprint.route('/config', methods=['GET'])
        @flask_login.login_required
        def config():
            return flask.render_template('plugins/config.html', current_app=flask.current_app, plugin=self.plugin,
                                         config=config_remove_credentials(self.plugin.active_config))

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
        return [{"text": "Config", "url": flask.url_for('plugins.'+self.blueprint.name+'.config')},
                {"text": "Log", "url": flask.url_for('plugins.'+self.blueprint.name+'.log')}]

    def get_title(self) -> str:
        """
        Retrieve the title for the connector UI.

        This method must be implemented by subclasses to provide a specific title.
        """
        raise NotImplementedError("Subclasses must provide get_title method")
