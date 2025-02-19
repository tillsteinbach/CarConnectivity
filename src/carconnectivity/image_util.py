"""Module containing custom json encoders for the carconnectivity package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

# pylint: disable=duplicate-code
SUPPORT_IMAGES = False
try:
    from PIL import Image
    SUPPORT_IMAGES = True
except ImportError:
    pass

SUPPORT_ASCII_IMAGES = False
try:
    import ascii_magic
    import shutil
    SUPPORT_ASCII_IMAGES = True
except ImportError:
    pass
# pylint: enable=duplicate-code

if TYPE_CHECKING:
    from typing import Optional, Tuple

if SUPPORT_IMAGES and SUPPORT_ASCII_IMAGES:
    class ASCIIModes(Enum):
        """
        Enum class representing different ASCII modes.

        Attributes:
            TERMINAL (str): Mode for terminal output.
            ASCII (str): Mode for plain ASCII output.
            HTML (str): Mode for HTML output.
        """
        TERMINAL = 'TERMINAL'
        ASCII = 'ASCII'
        HTML = 'HTML'

    def image_to_ASCII_art(img: Image.Image, columns: int = 0, mode=ASCIIModes.TERMINAL) -> str:  # pylint: disable=invalid-name
        """
        Converts an image to ASCII art.

        Args:
            img (Image): The input image to be converted.
            columns (int, optional): The number of columns for the ASCII art. Defaults to 0, which uses the terminal width.
            mode (ASCIIModes, optional): The mode for the ASCII art output. Can be ASCIIModes.TERMINAL, ASCIIModes.ASCII, or ASCIIModes.HTML.
            Defaults to ASCIIModes.TERMINAL.

        Returns:
            str: The resulting ASCII art as a string.
        """
        bbox: Optional[Tuple[int, int, int, int]] = img.getbbox()

        # Crop the image to the contents of the bounding box
        image: Image.Image = img.crop(bbox)

        # Determine the width and height of the cropped image
        (width, height) = image.size

        # Create a new image object for the output image
        cropped_image: Image.Image = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # pyright: ignore[reportPossiblyUnboundVariable]

        # Paste the cropped image onto the new image
        cropped_image.paste(image, (0, 0))

        if columns == 0:
            columns = shutil.get_terminal_size()[0]  # pyright: ignore[reportPossiblyUnboundVariable]

        if mode == ASCIIModes.ASCII:
            return ascii_magic.from_pillow_image(cropped_image).to_ascii(columns=columns, monochrome=True)  # pyright: ignore[reportPossiblyUnboundVariable]
        if mode == ASCIIModes.HTML:
            return ascii_magic.from_pillow_image(cropped_image).to_html(columns=columns)  # pyright: ignore[reportPossiblyUnboundVariable]
        return ascii_magic.from_pillow_image(cropped_image).to_ascii(columns=columns)  # pyright: ignore[reportPossiblyUnboundVariable]
