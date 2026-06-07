# Local run

This fork uses visible local Chrome automation so SMS verification after Douyin QR login can be completed on the same machine.

## Requirements

- Python 3.10+
- Node.js 18+
- Google Chrome
- Chromedriver matching your Chrome version, available on `PATH`

Optional environment variables:

```bash
CHROME_BINARY=/path/to/chrome
CHROMEDRIVER_PATH=/path/to/chromedriver
CHROME_PROFILE_DIR=./chrome-profile
PORT=9844
```

## Windows

```powershell
.\start-backend.ps1
npm install
npm run dev
```

Open `http://localhost:5173`.

## Linux

```bash
chmod +x ./start-backend.sh
./start-backend.sh
npm install
npm run dev
```

Open `http://localhost:5173`.

Default admin login:

```text
admin / 123456
```
