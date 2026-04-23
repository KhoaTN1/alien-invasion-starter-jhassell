class Settings:
    """A simple settings class for game screen configuration."""

    def __init__(self, width=1600, height=900, bg_color=(0, 0, 0)):
        """Initialize screen settings.

        Args:
            width (int): Screen width in pixels.
            height (int): Screen height in pixels.
            bg_color (tuple): RGB background color.
        """
        self.screen_width = width
        self.screen_height = height
        self.bg_color = bg_color
