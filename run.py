"""
Legacy application entry point for backward compatibility.

This file maintains compatibility with existing deployment scripts
that might still reference run.py. For new deployments, use run_new.py
or update to import from the app package directly.
"""

import os
import warnings
from app import create_app

# Warn about deprecated usage
warnings.warn(
    "run.py is deprecated. Please use run_new.py or import from 'app' package directly.",
    DeprecationWarning,
    stacklevel=2
)

if __name__ == "__main__":
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    port = int(os.environ.get("PORT", 5000))
    debug = config_name == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
