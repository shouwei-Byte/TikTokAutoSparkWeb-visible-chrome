# Fork notes

This repository packages the server-tested visible Chrome version of TikTokAutoSparkWeb.

Changes in this version:

- Uses Chrome/Selenium instead of the original fixed Windows Edge driver path.
- Runs the browser visibly by default so Douyin QR login and SMS verification can be completed manually.
- Supports `CHROME_BINARY`, `CHROMEDRIVER_PATH`, `CHROME_PROFILE_DIR`, and `PORT` environment variables.
- Adds `requirements.txt`, `start-backend.ps1`, `start-backend.sh`, and `LOCAL_RUN.md`.
- Keeps browser profile, local drivers, virtual environments, build output, and passwords out of git.

Original upstream: `DkoBot/TikTokAutoSparkWeb`.
