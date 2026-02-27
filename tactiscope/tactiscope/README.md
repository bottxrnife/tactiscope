# TactiScope

An autonomous sports tactics auto-breakdown web application built for the AI Agents Hackathon. 

TactiScope orchestrates three distinct AI models to completely automate the video analysis process:
1. **Reka Vision**: Generates short, actionable highlight clips directly from full match videos.
2. **Fastino GLiNER-2**: Extracts structured JSON tactical patterns and classifies events (goals, high press, transitions) from commentary texts.
3. **Yutori Research**: Autonomously browses the web to scout real-time team context, recent form, and league standings.

## Architecture

The project is structured as a monorepo containing a modern React frontend and a Python backend.

- **Frontend (`/frontend`)**: Next.js 16 (React 19) + Tailwind CSS + shadcn/ui components. Polling-based UI for async autonomous pipeline monitoring.
- **Backend (`/backend`)**: FastAPI + Python 3.9+ utilizing `asyncio` for parallel API orchestration.

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- API Keys for Reka, Fastino (Pioneer), and Yutori

### 1. Backend Setup

```bash
cd backend

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# You must create a .env file based on the provided keys
```

**`backend/.env` file:**
```env
REKA_API_KEY=your_reka_key_here
FASTINO_API_KEY=your_fastino_key_here
YUTORI_API_KEY=your_yutori_key_here
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Running the Application

You need to run both the backend and frontend servers simultaneously.

**Terminal 1 (Backend):**
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`.

## Testing & Simulation

The backend includes tools to verify API connectivity and simulate the full autonomous pipeline without hitting the frontend.

### API Sanity Check
Validates authentication and basic functionality for all three AI APIs.
```bash
cd backend
python3 -m tests.test_apis
```

### Full E2E Simulation
Runs the full orchestration pipeline end-to-end and prints the raw data outputs, including highlight clips, structured tactical events, and the final generated coach's briefing markdown.
```bash
cd backend
python3 -m tests.simulate_run
```

## How It Works (The Pipeline)

When a user submits a match via the UI, the FastAPI backend orchestrator kicks off a parallel pipeline:
1. **Parallel Kickoff**: Reka Vision starts downloading and processing the video URL for clips, while Yutori immediately begins researching the match context.
2. **Annotation Phase**: Once Reka returns clips, the clips' generated titles and captions are fed into Fastino GLiNER-2 to extract structured tactical entities (players, events) and classify the plays (e.g., transition, set piece).
3. **Synthesis**: The backend waits for the Yutori web research task to complete.
4. **Final Briefing**: The final structured JSON from Fastino, the video URLs from Reka, and the markdown research from Yutori are dynamically combined into a comprehensive "Coach's Briefing" presented on the dashboard.
