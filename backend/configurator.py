"""Config file manager"""
import configparser
import os


class State:
    """Configuration class"""
    CONFIG_ERROR: str = "CONFIG_ERROR"


class Config(State):
    """Class managing configuration file."""
    def __init__(self) -> None:
        """Init class"""
        super().__init__()
        self.path = os.path.expanduser('~\\config.ini')
        self.config = configparser.ConfigParser()
        self.__configuration: dict = {}
        self.__mode: str = "r+"

    def mode(self) -> None:
        """Get proper mode"""
        if os.path.isfile(self.path):
            self.__mode = "r+"
        else:
            self.__mode = "w+"

    def read_config(self) -> None:
        """Read config file."""
        if os.path.isfile(self.path):
            try:
                self.config.read(self.path)

                destination = self.config.get("Settings", "destination")
                self.__configuration["destination"] = destination
                interval = self.config.get("Settings", "interval")
                self.__configuration["interval"] = interval
                quality = self.config.get("Settings", "quality")
                self.__configuration["quality"] = quality

                return self.__configuration

            except configparser.NoSectionError:
                self.remove_config()
                self.create_config(path=None, interval=None, quality=None)
                return State.CONFIG_ERROR

            except configparser.ParsingError:
                self.remove_config()
                self.create_config(path=None, interval=None, quality=None)
                return State.CONFIG_ERROR

        return State.CONFIG_ERROR

    def create_config(self, path, interval: int, quality: int):
        """Create/edit config file."""
        try:
            self.config = configparser.ConfigParser()
            self.config.add_section('Settings')
            self.config.set("Settings", "destination", str(path))
            self.config.set("Settings", "interval", str(interval))
            self.config.set("Settings", "quality", str(quality))

            # Writing our configuration file to 'config.ini'.
            self.mode()
            with open(self.path, self.__mode) as configuration:
                self.config.write(configuration)

            # Make file hidden.
            os.system("attrib +h {}".format(self.path))

        except OSError as error:
            print("Configurator - create_config {}".format(error))

    def remove_config(self) -> None:
        """Remove config file."""
        try:
            os.remove(self.path)

        except OSError as error:
            print("Configurator - remove_config {}".format(error))
