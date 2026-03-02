"""Display brightness and screen blanking control for SpoolBuddy kiosk."""

import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)

BACKLIGHT_BASE = Path("/sys/class/backlight")


class DisplayControl:
    def __init__(self):
        self._backlight_path = self._find_backlight()
        self._max_brightness = self._read_max_brightness()
        self._blank_timeout = 0  # seconds, 0 = disabled
        self._last_activity = time.monotonic()
        self._blanked = False

        if self._backlight_path:
            logger.info("Backlight found: %s (max=%d)", self._backlight_path, self._max_brightness)
        else:
            logger.info("No DSI backlight found, brightness control unavailable")

    def _find_backlight(self) -> Path | None:
        if not BACKLIGHT_BASE.exists():
            return None
        for entry in BACKLIGHT_BASE.iterdir():
            brightness_file = entry / "brightness"
            if brightness_file.exists():
                return entry
        return None

    def _read_max_brightness(self) -> int:
        if not self._backlight_path:
            return 100
        try:
            return int((self._backlight_path / "max_brightness").read_text().strip())
        except Exception:
            return 255

    @property
    def has_backlight(self) -> bool:
        return self._backlight_path is not None

    def set_brightness(self, pct: int):
        """Set backlight brightness (0-100%). No-op if no backlight."""
        if not self._backlight_path:
            return
        pct = max(0, min(100, pct))
        value = round(self._max_brightness * pct / 100)
        try:
            (self._backlight_path / "brightness").write_text(str(value))
            logger.debug("Brightness set to %d%% (%d/%d)", pct, value, self._max_brightness)
        except Exception as e:
            logger.warning("Failed to set brightness: %s", e)

    def set_blank_timeout(self, seconds: int):
        """Set screen blank timeout in seconds. 0 = disabled."""
        self._blank_timeout = max(0, seconds)

    def wake(self):
        """Wake screen on activity (NFC tag, scale weight change)."""
        self._last_activity = time.monotonic()
        if self._blanked:
            self._unblank()

    def tick(self):
        """Called periodically from heartbeat loop. Blanks screen if idle."""
        if self._blank_timeout <= 0:
            if self._blanked:
                self._unblank()
            return
        idle = time.monotonic() - self._last_activity
        if not self._blanked and idle >= self._blank_timeout:
            self._blank()

    def _blank(self):
        try:
            subprocess.run(["wlopm", "--off", "*"], capture_output=True, timeout=5)
            self._blanked = True
            logger.debug("Screen blanked after idle timeout")
        except Exception as e:
            logger.warning("Failed to blank screen: %s", e)

    def _unblank(self):
        try:
            subprocess.run(["wlopm", "--on", "*"], capture_output=True, timeout=5)
            self._blanked = False
            logger.debug("Screen unblanked")
        except Exception as e:
            logger.warning("Failed to unblank screen: %s", e)
