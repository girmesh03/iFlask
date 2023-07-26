from configparser import ConfigParser


class Configuration:
    """A class for handling configuration files using ConfigParser"""

    def __init__(self, config_file):
        """
        Initialize the Configuration object.

        Args:
            config_file (str): The path to the configuration file.
        """
        self.config_file = config_file
        self.config = ConfigParser()
        self.config.read(self.config_file)

    def get_value(self, section, key):
        """
        Retrieve a value from the configuration file.

        Args:
            section (str): The section in the configuration file.
            key (str): The key of the value to retrieve.

        Returns:
            str: The value associated with the given section and key.
        """
        return self.config.get(section, key)

    def set_value(self, section, key, value):
        """
        Set a value in the configuration file.

        If the section doesn't exist, it will be created.

        Args:
            section (str): The section in the configuration file.
            key (str): The key of the value to set.
            value (str): The value to set.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def save_changes(self):
        """
        Save the changes made to the configuration file.
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def remove_section(self, section):
        """
        Remove a section from the configuration file.

        Args:
            section (str): The section to remove.
        """
        self.config.remove_section(section)

    def remove_key(self, section, key):
        """
        Remove a key from a section in the configuration file.

        Args:
            section (str): The section where the key is located.
            key (str): The key to remove.
        """
        self.config.remove_option(section, key)
