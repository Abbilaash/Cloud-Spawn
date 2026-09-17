# CloudSpawn

Dynamic Serverless Task Orchestration for Autonomous AI Agents

---

## Setup & Execution Commands

### 1. Clone CloudSpawn Repository
```bash
git clone https://github.com/Abbilaash/Cloud-Spawn.git
cd Cloud-Spawn
```

### 2. Install Backend Dependencies
```bash
cd Backend
python -m venv venv
# Activate virtual environment (Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
cd ..
```

### 3. Install Frontend Dependencies
```bash
cd Frontend
npm install   # or pnpm install
cd ..
```

### 4. Clone & Install Formicx Runtime
```bash
git clone https://github.com/Formicx/formicx.git
cd formicx
pip install -r requirements.txt
pip install -e .
cd ..
```

### 5. Run Formicx Daemon
```bash
formicxd
```

### 6. Run Formicx MCP Server
```bash
formicx mcp start
```

### 7. Formicx MCP Integration (Antigravity / VS Code / GitHub Copilot)

Add the following configuration to your IDE's MCP settings file (`mcp_config.json`):

```json
{
  "mcpServers": {
    "formicx": {
      "command": "formicx",
      "args": [
        "mcp",
        "start"
      ]
    }
  }
}
```

---

## Running Applications

### Run Backend Server
```bash
cd Backend
uvicorn app.main:app --reload
```

### Run Frontend Development Server
```bash
cd Frontend
npm run dev   # or pnpm dev
```
