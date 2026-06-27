import logging
from pathlib import Path

# ==========================================================
# APPLICATION LOGGING CONFIGURATION
# ==========================================================
# Centralizes application logging.
#
# During local development:
#   - Logs are displayed in the terminal.
#   - Logs are also written to logs/application.log.
#
# During AWS deployment, this module can be updated to send
# logs to CloudWatch without changing the application code.
# ==========================================================

# Create the logs directory if it does not already exist.
log_directory = Path("logs")
log_directory.mkdir(exist_ok=True)

# Log file location.
log_file = log_directory / "application.log"

# Configure the application logger.
logger = logging.getLogger("mecandjeo-school")
logger.setLevel(logging.INFO)

# Prevent duplicate log entries if the application reloads.
if not logger.handlers:

    # Display logs in the terminal.
    console_handler = logging.StreamHandler()

    # Write logs to logs/application.log.
    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    # Shared log format.
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)