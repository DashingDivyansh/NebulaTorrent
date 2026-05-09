# NebulaTorrent

Modern decentralized torrent search desktop application.

## Structure

- `src/frontend`: React + TypeScript + TailwindCSS
- `src/backend`: Python FastAPI (Dispatcher + Plugins)
- `src/tauri`: Tauri Desktop Wrapper

## Getting Started

### 1. Start the Backend
```bash
cd src/backend
# Create venv and install dependencies
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### 2. Start the Frontend (Web Mode)
```bash
cd src/frontend
npm install
npm run dev
```

### 3. Start Tauri (Desktop Mode)
*Requires Rust and Cargo*
```bash
cd src/tauri
npm install
npx tauri dev
```

## Features Implemented

- **Multi-indexer Search**: Search SolidTorrents and Nyaa simultaneously.
- **Async Dispatcher**: Parallel plugin execution using `asyncio` and `httpx`.
- **Plugin Architecture**: Easily add new plugins by inheriting from `BasePlugin`.
- **Modern UI**: Clean interface built with React and TailwindCSS.
- **Magnet Support**: Copy magnet links or send directly to qBittorrent.
- **Sorting & Filtering**: Sort by seeders, size, name, etc. Filter by category.
- **qBittorrent Integration**: Add torrents directly via WebUI API.
