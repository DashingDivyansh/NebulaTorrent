# NebulaTorrent

**NebulaTorrent** is a modern, decentralized torrent search desktop application. It provides a unified, blazing-fast interface to search across multiple torrent indexers simultaneously, inspired by the versatility of qBittorrent's search engine but built with a high-performance modern tech stack.

## 🚀 Key Features

- **Decentralized Plugin Architecture:** Easily extensible backend that supports multiple torrent indexers (BTDigg, TPB, Nyaa, EZTV, YTS, etc.) via a unified plugin system.
- **High-Performance Backend:** Built with **FastAPI** for asynchronous, non-blocking search requests.
- **Modern Desktop Experience:** A sleek, responsive UI built with **React**, **TypeScript**, and **Tailwind CSS**, packaged as a lightweight native desktop app using **Tauri**.
- **Smart Ranking & Filtering:** Real-time sorting and filtering of results to find exactly what you need.
- **Proxy & Security:** Built-in support for global proxies and user-agent rotation to ensure reliable access to indexers.
- **Decoupled Design:** The backend API can run independently of the frontend, allowing for headless or remote search setups.

## 🏗️ Architecture

- **Frontend (`src/frontend$b):** A Vite-powered React application using Zustand for state management and Tailwind CSS for styling.
- **Backend (`src/backend$b):** A Python FastAPI server that manages the `SearchDispatcher`, handling concurrent plugin execution and result aggregation.
- **Plugins (`src/backend/plugins$b):** Modular scrapers and API integrations for various torrent sites.
- **Desktop Wrapper (`src/tauri$b):** Tauri integration providing native OS windows and system tray support.

## 🛠️ Tech Stack

- **Languages:** Python 3.10+, TypeScript, Rust (via Tauri)
- **Frameworks:** FastAPI, React 18
- **Styling:** Tailwind CSS
- **Database:** SQLite (for history and settings)
- **Communication:** REST API / HTTPX

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- Rust (for building the Tauri desktop app)

### 2. Setup the Backend
```bash
cd src/backend
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3. Setup the Frontend
```bash
cd src/frontend
npm install
npm run dev
```

### 4. Run the Desktop App (Tauri)
```bash
cd src/tauri
npm install
npm run tauri dev
```

## 🔌 Supported Indexers (Plugins)

NebulaTorrent currently ships with support for:
- **Movies/TV:** TPB, YTS, EZTV, TorrentGalaxy
- **Anime:** Nyaa
- **Games:** FitGirl
- **General:** BTDigg, LimeTorrents, SolidTorrents, GloTorrents, Knaben

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
