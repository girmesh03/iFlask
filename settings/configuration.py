"""A module for handling configuration files using ConfigParser."""

from configparser import ConfigParser


class Configuration:
    """A class for handling configuration files using ConfigParser"""

    def __init__(self, config_file):
        """Initialize the Configuration class."""
        self.config_file = config_file
        self.config = ConfigParser()
        self.config.read(self.config_file)

    def get_value(self, section, key):
        """Get a value from the configuration file."""
        return self.config.get(section, key)

    def set_value(self, section, key, value):
        """Set a value in the configuration file."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def save_changes(self):
        """Save the changes to the configuration file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def remove_section(self, section):
        """Remove a section from the configuration file."""
        self.config.remove_section(section)

    def remove_key(self, section, key):
        """Remove a key from a section in the configuration file."""
        self.config.remove_option(section, key)
