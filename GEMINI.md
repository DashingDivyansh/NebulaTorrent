# NebulaTorrent Architecture and Development Guidelines

## Project Context
**NebulaTorrent** is a decentralized torrent search toolkit with a FastAPI backend, a React/Vite frontend, and a Tauri desktop wrapper.

### Current Status (May 2026)
- **Live on GitHub:** [https://github.com/DashingDivyansh/NebulaTorrent](https://github.com/DashingDivyansh/NebulaTorrent)
- **Tech Stack:** FastAPI, React (Zustand/Tailwind), Tauri (Rust), SQLite.
- **Documentation:** README overhauled with detailed architectural mapping.

## Architectural Rules

### 1. Plugin-Dispatcher Pattern
- All search logic must be encapsulated in a class inheriting from \BasePlugin\ (\src/backend/plugins/base.py\).
- The \SearchDispatcher\ (\src/backend/search/dispatcher.py\) handles the orchestration of these plugins. Never call plugins directly from the API layer.
- Plugins must use \httpx.AsyncClient\ for all network requests to maintain the non-blocking nature of the FastAPI server.

### 2. Desktop Integration (Tauri)
- The frontend (\src/frontend\) should remain decoupled from Tauri-specific APIs where possible.
- Use environment variables or specific build commands to toggle between "Web Mode" and "Desktop Mode".

### 3. State Management
- **Backend:** Prefer Pydantic models for data validation and API responses.
- **Frontend:** Use Zustand (\src/frontend/src/store/useSearchStore.ts\) for global state. Do not use complex React Context for search results to avoid unnecessary re-renders.

## Graphify Usage
This project has a graphify knowledge graph at \graphify-out/\.
- Before answering architecture or codebase questions, read \graphify-out/GRAPH_REPORT.md\ for god nodes and community structure.
- For cross-module "how does X relate to Y" questions, prefer \graphify query\ over grep.
