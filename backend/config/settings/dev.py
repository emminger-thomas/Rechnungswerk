import os

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "rechnungswerk"),
        "USER": os.environ.get("DB_USER", "rechnungswerk_app"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "rechnungswerk_dev_pw"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# WeasyPrint needs the native GTK/Pango libraries on its DLL search path on
# Windows. The standalone GTK3 runtime (tschoonj.GTKForWindows via winget)
# installs into this default location; add its bin dir to PATH if present
# so `import weasyprint` succeeds without a manual environment setup step.
_gtk_bin = r"C:\Program Files\GTK3-Runtime Win64\bin"
if os.path.isdir(_gtk_bin) and _gtk_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _gtk_bin + os.pathsep + os.environ.get("PATH", "")
