"""Screen capture function"""

import os
from datetime import datetime
from PIL import ImageGrab


class Screen:
    """Class managing screenshooter job."""
    def __init__(self, path, quality: int, interval: int) -> None:
        """Init class"""

        self.path = self.origin_path = path
        self.quality = quality
        self.interval = interval

    def get_file(self) -> None:
        """Generate file name."""
        now = datetime.now()
        return os.path.join(self.origin_path, (now.strftime("%m-%d-%Y-%H-%M-%S") + ".png"))

    def get_screen(self) -> None:
        """Make screenshot."""
        screen = ImageGrab.grab()
        screen.save(self.path, "PNG",
                    optimize=True,
                    quality=self.quality)

    def start_job(self) -> None:
        """Main function."""
        self.path = self.get_file()
        self.get_screen()
