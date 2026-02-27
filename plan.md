# Sports Tactics Auto‑Breakdown Assistant – Implementation Plan

## 1. MVP Goal and Constraints

Build a web app where a user pastes a match video URL (or uploads a clip), enters API keys for **Yutori**, **Fastino GLiNER‑2**, and **Reka Vision**, clicks **“Analyze Match”**, and sees:

- A highlight playlist generated from the match video (clips + tags).
- A simple tactical summary (offense/defense patterns, key plays) extracted from commentary.
- Basic context from the web (team, league, recent form) pulled via Yutori.

The whole pipeline should run automatically after the user submits the form, so the hackathon judges see a single-shot autonomous flow.

## 2. Core Architecture Overview

Recommended stack for a fast hackathon build:

- **Frontend:** Next.js/React (or plain React + Vite) single-page UI.
- **Backend:** Node.js with Express (or Fastify) for simplicity.
- **Storage:** In-memory data structures for MVP; optional temp disk for downloaded video.
- **APIs:**
  - Reka Vision API for video upload, highlight clip generation, video Q&A.[^1][^2][^3]
  - Fastino GLiNER‑2 `/gliner-2` inference endpoint for schema-based extraction from commentary/transcripts.[^4][^5][^6]
  - Yutori Research API (and optionally Browsing) via Python SDK or direct HTTP for team/league stats.[^7][^8][^9][^10][^11]

### High-Level Data Flow

1. User enters match video URL (e.g., YouTube) and team names, plus API keys.
2. Backend kicks off an **analyzeMatch** job:
   - Calls **Reka Vision** to generate highlight clips from the video URL.
   - Obtains or assumes commentary text for the same match (from YouTube transcript, manual input, or a small mock).
   - Sends commentary segments to **Fastino GLiNER‑2** for structured extraction (who scored, event type, minute, etc.).
   - Calls **Yutori Research** to fetch team/league context.
3. Backend merges all outputs into a single JSON `MatchAnalysis` object (highlights + structured events + web context).
4. Frontend polls for job completion and then renders:
   - Video highlight list with tags.
   - A 1‑page “coach’s briefing” summary.
   - Side panel with Yutori-derived context.

## 3. Reka Vision Integration Details

### Key Endpoints

The Vision API supports video upload/management, video Q&A, metadata tagging, and highlight clips.[^1]

Core pieces you need:

- **Upload/Reference Video:**
  - Use `POST /v1/videos/upload` if you are uploading a local file.
  - If using YouTube or another URL, some Vision workflows (including clips) accept `video_urls` directly.[^2][^1]
- **Highlight Clip Generation:**
  - `POST https://vision-agent.api.reka.ai/v1/clips` with:
    - `video_urls`: `["https://www.youtube.com/watch?v=..."]`
    - `prompt`: short description of the type of moments you want (e.g., "goals, shots on target, big chances").
    - `generation_config`: number/duration of clips.
    - `rendering_config`: subtitles, aspect ratio, resolution.[^12][^2]
  - Poll via `GET /v1/clips/{id}` until `status` is `completed`.[^2]
- **Video Q&A:**
  - Use the Video Q&A endpoint to ask questions against indexed videos once they are processed (e.g., "Show all clips where the defense is in a zone" or "Where does Player 7 lose the ball?"), via `/v1/qa/chat` or similar.[^3][^1]

### Minimal MVP Usage

For the hackathon vertical slice:

- Accept **a YouTube URL or local upload**.
- Call **`POST /v1/clips`** once with:
  - `prompt`: "Create short clips of all important plays, goals, and turnovers in this match."
  - `generation_config`: `{ template: "moments", num_generations: 3, max_duration_seconds: 40 }`.
  - `rendering_config`: `{ subtitles: true, aspect_ratio: "16:9", resolution: 720 }`.[^12][^2]
- Store the returned `id` and poll until you get a list of `output` clip URLs.
- Surface those clip URLs in the UI with basic labels: `Clip 1`, `Clip 2`, etc.

Later improvement: use Video Q&A (`/v1/qa/chat`) to label each clip by asking Reka questions about it, but for day-one MVP you can infer labels from text metadata or use generic labels plus Fastino-derived tags.[^3][^1]

## 4. Fastino GLiNER‑2 Integration Details

### Capabilities

GLiNER‑2 is a schema-based information extraction model that supports:

- Named Entity Recognition (players, teams, locations).
- Text classification (offense vs defense, play type, etc.).
- Structured JSON extraction in a single forward pass.[^6][^4]

The hosted API exposes a single inference endpoint:

- `POST /gliner-2` – runs schema-driven extraction, classification, or JSON parsing on your text.[^5][^6]

### Request Shape (Conceptual)

You define:

- `text`: a commentary snippet, video description, or your own coarse transcription.
- `schema`: an object describing what you want extracted (entities, fields).
- `task_type`: e.g., `extract_json` or `extract_entities`.[^6]

Example tactical schema (pseudocode):

```json
{
  "task_type": "extract_json",
  "text": "In the 67th minute, Smith scores after a quick counter attack on the right wing.",
  "schema": {
    "minute": "integer",
    "team": "string",
    "player": "string",
    "event_type": "enum[goal, shot, turnover, foul, assist]",
    "tactical_pattern": "enum[counter_attack, set_piece, high_press, low_block, transition]"
  },
  "threshold": 0.5
}
```

The API returns a structured JSON object with extracted values and confidence scores.[^5][^6]

### Where to Get Text

For MVP you can avoid implementing your own ASR by using:

- Video descriptions + manual commentary text.
- A short manually written “commentary script” aligned roughly to the match clip.

Later, you can:

- Use YouTube auto-generated transcripts for public videos.
- Or plug in a generic ASR (Whisper, Deepgram, etc.) to feed real commentary into GLiNER‑2.

### Minimal MVP Usage

- For each highlight clip returned by Reka, associate a short commentary text (even if mocked) describing that moment.
- Send that text to GLiNER‑2 with a schema like the example above.
- Use the response to:
  - Tag each clip with event type and tactical pattern.
  - Build a “match stats” summary (e.g., number of counter-attacks, set pieces, turnovers).

## 5. Yutori Integration Details

### Capabilities

Yutori exposes four key APIs via its Python SDK and HTTP:

- **n1:** pixels-to-actions model for browser-like navigation.
- **Browsing:** one-off automation tasks in a cloud browser.
- **Research:** deep web research using 100+ MCP tools and subagents.
- **Scouting:** recurring monitoring tasks (not needed for MVP).[^8][^9][^10][^7]

For this project, focus on **Research** (and optionally **Browsing**):

- Research API:
  - `client.research.create(query=..., user_timezone=...)` to launch a task.
  - Poll with `client.research.get(task_id)` until `status` is `succeeded`.[^9][^11][^8]
- Browsing API:
  - Use for specific page scraping (e.g., scraping league table from a single site), but you can skip this in MVP and just rely on Research.

### Minimal MVP Usage

- When the user submits a match, call Yutori Research with a query like:

  > "Provide a short scouting summary for the soccer match between Team A and Team B, including league context, recent form, and key players, in 3 bullet points."[^7][^8][^9]

- Parse Yutori’s structured result for a small set of fields (e.g., `summary`, `key_players`, `recent_form`) and display them in a side panel and at the top of the “coach’s briefing.”

This shows real **autonomy and web interaction** without overcomplicating your architecture.

## 6. Project Structure for WindSurf / VS Code

A simple mono-repo layout that plays nicely with WindSurf / VS Code:

```text
sports-tactics-assistant/
  .env.example
  package.json
  README.md

  backend/
    package.json
    src/
      index.ts
      routes/
        analyzeMatch.ts
      services/
        rekaVision.ts
        fastino.ts
        yutori.ts
      types/
        MatchAnalysis.ts

  frontend/
    package.json
    next.config.mjs
    src/
      pages/
        index.tsx
      components/
        ApiKeyForm.tsx
        MatchForm.tsx
        AnalysisStatus.tsx
        HighlightList.tsx
        CoachBriefing.tsx
        TeamContextPanel.tsx
      lib/
        api.ts
```

### Environment Variables

Use `.env` at repo root, loaded by both backend and frontend where needed:

```text
REKA_API_KEY=...
FASTINO_API_KEY=...
YUTORI_API_KEY=...
NODE_ENV=development
BACKEND_URL=http://localhost:4000
```

Backend reads keys directly from `process.env`. Frontend only sends a boolean "keys configured" and never exposes raw secrets to the browser.

## 7. Backend Endpoints and Logic

### `POST /api/analyze` (main orchestration route)

Request body (from frontend):

```json
{
  "videoUrl": "https://www.youtube.com/watch?v=...",
  "homeTeam": "Team A",
  "awayTeam": "Team B",
  "sport": "soccer"
}
```

High-level steps in `analyzeMatchHandler`:

1. **Validate** input, check that API keys exist on server.
2. **Kick off Reka clip generation** (async):
   - `const clipJobId = await reka.createHighlightJob(videoUrl)`.
3. **Start Yutori research** in parallel:
   - `const yutoriTaskId = await yutori.createResearchTask(homeTeam, awayTeam)`.
4. **Obtain/construct commentary text:**
   - For MVP, call a helper that returns a mock commentary per potential clip index.
5. **Poll for Reka clips:**
   - `const clips = await reka.getClips(clipJobId)`.
6. For each `clip`:
   - Build a short commentary snippet (from real transcript or mock).
   - Call Fastino GLiNER‑2:
     - `const tacticalInfo = await fastino.analyzeCommentary(snippet)`.
7. **Poll Yutori research results** and parse into `teamContext`.
8. **Assemble `MatchAnalysis` JSON**:

```ts
interface HighlightClip {
  id: string;
  url: string;
  summary: string;
  eventType: string;          // goal, shot, turnover, etc.
  tacticalPattern: string;    // counter_attack, set_piece, etc.
}

interface TeamContext {
  league: string;
  recentForm: string;
  keyPlayers: string[];
  notes: string;
}

interface MatchAnalysis {
  homeTeam: string;
  awayTeam: string;
  highlights: HighlightClip[];
  briefingMarkdown: string;
  context: TeamContext;
}
```

9. **Store analysis in memory** keyed by a `jobId`, return that `jobId` immediately:

```json
{ "jobId": "abc123" }
```

### `GET /api/analyze/:jobId`

Returns the `MatchAnalysis` object once ready (or status `processing`). Frontend polls every 2–3 seconds until `status === 'done'`.

## 8. Service Modules (Backend)

### `rekaVision.ts`

Responsibilities:

- Wrap `POST /v1/clips` and `GET /v1/clips/{id}`.[^2][^12]
- Optionally later: wrap Video Q&A endpoints.[^1][^3]

Pseudocode:

```ts
const BASE_URL = "https://vision-agent.api.reka.ai";

export async function createHighlightJob(videoUrl: string): Promise<string> {
  const res = await fetch(`${BASE_URL}/v1/clips`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": process.env.REKA_API_KEY!,
    },
    body: JSON.stringify({
      video_urls: [videoUrl],
      prompt: "Create short clips showing the most important plays, goals, and turnovers.",
      generation_config: {
        template: "moments",
        num_generations: 3,
        max_duration_seconds: 40,
      },
      rendering_config: { subtitles: true, aspect_ratio: "16:9", resolution: 720 },
    }),
  });
  const data = await res.json();
  return data.id;
}

export async function getClips(jobId: string) {
  const res = await fetch(`${BASE_URL}/v1/clips/${jobId}`, {
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": process.env.REKA_API_KEY!,
    },
  });
  const data = await res.json();
  return data; // contains status + output clip URLs
}
```

### `fastino.ts`

Wraps `POST /gliner-2` with your tactical schema.[^4][^5][^6]

Key: keep text short (< 8 KB) per call for best latency.[^6]

Pseudocode:

```ts
const FASTINO_URL = "https://api.fastino.ai/gliner-2";

export async function analyzeCommentary(snippet: string) {
  const schema = {
    minute: "integer",
    team: "string",
    player: "string",
    event_type: "enum[goal, shot, turnover, foul, assist]",
    tactical_pattern: "enum[counter_attack, set_piece, high_press, low_block, transition]",
  };

  const res = await fetch(FASTINO_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.FASTINO_API_KEY}`,
    },
    body: JSON.stringify({
      text: snippet,
      schema,
      task_type: "extract_json",
      threshold: 0.5,
    }),
  });

  return await res.json();
}
```

### `yutori.ts`

You can either:

- Use the **Python SDK** in a small sidecar service (best documented).[^8][^9]
- Or call HTTP directly from Node if you have the REST endpoints.

Simplest for hackathon: create a tiny Python script or service that exposes `GET /yutori-scout?homeTeam=...&awayTeam=...` and uses the SDK example to call `client.research.create` + `client.research.get`.

Example (Python sidecar, abbreviated):[^9][^8]

```python
from fastapi import FastAPI
from yutori import YutoriClient
import time

app = FastAPI()
client = YutoriClient()  # reads YUTORI_API_KEY

@app.get("/yutori-scout")
def scout(home_team: str, away_team: str):
    query = (
      f"Provide a brief match context and scouting summary for a soccer match "
      f"between {home_team} and {away_team}. Include league, recent form, and key players."
    )
    task = client.research.create(query=query, user_timezone="America/Los_Angeles")
    task_id = task["task_id"]
    while True:
        result = client.research.get(task_id)
        if result["status"] in ("succeeded", "failed"):
            break
        time.sleep(5)
    return result
```

Your Node backend can call this local service and normalize its output.

## 9. Frontend UI Flow

Page: `/` (single-page app)

Sections:

1. **API Key Form (`ApiKeyForm`)**
   - Fields for Reka, Fastino, Yutori API keys.
   - On submit: POST to backend `/api/configure-keys` (optional) or just store locally in `.env` and use this form as a visual “configured” check.

2. **Match Form (`MatchForm`)**
   - Inputs: video URL, home team, away team, sport (dropdown: soccer/basketball).
   - Button: **Analyze Match** → calls `/api/analyze`.

3. **Analysis Status (`AnalysisStatus`)**
   - When you get `jobId`, start polling `/api/analyze/:jobId`.
   - Show spinner and messages like “Generating highlights with Reka”, “Extracting tactics with Fastino”, “Fetching team context via Yutori”.

4. **Results Section**
   - **HighlightList:** List of clips with thumbnail (if available) and labels from Fastino.
   - **CoachBriefing:** Render Markdown `briefingMarkdown` via a simple markdown renderer.
   - **TeamContextPanel:** Show league, recent form, key players from Yutori.

This gives judges a clear story arc from inputs to autonomous output.

## 10. Today’s Build Checklist (One‑Shot MVP)

Your goal for today: after wiring .env with the three API keys, you can:

1. Run `pnpm install` (or `npm install`) in root + backend + frontend.
2. Start backend on port 4000, frontend on 3000.
3. Open `http://localhost:3000`, paste a **demo match URL**, enter teams, and click **Analyze**.
4. Wait ~30–90 seconds and see clips + a simple briefing.

Concrete steps:

1. **Repo Skeleton**
   - Initialize `sports-tactics-assistant` with `backend` and `frontend` folders.
   - Add `tsconfig`, simple `Express` server, and basic Next.js page.

2. **Environment & Config**
   - Implement a small `config.ts` that reads `REKA_API_KEY`, `FASTINO_API_KEY`, `YUTORI_API_KEY` and throws helpful errors if missing.

3. **Reka Service First**
   - Implement `rekaVision.ts` with `createHighlightJob` and `getClips`.
   - Hard-code a single YouTube URL and test that clip generation works via a simple CLI script.

4. **Fastino Service**
   - Implement `fastino.ts` with a very small schema.
   - Test locally on a fake commentary string.

5. **Yutori Sidecar (Optional Same Day)**
   - Implement the small FastAPI service if you go the Python route.
   - Or, if Yutori’s HTTP endpoints are known, call them directly from Node using the Research API pattern.[^11][^8][^9]

6. **Wire `/api/analyze`**
   - Parallelize Reka + Yutori tasks using `Promise.all`.
   - After clips are ready, annotate each with a single Fastino call.

7. **Frontend**
   - Implement simple forms and polling logic.
   - First render: just a JSON dump of `MatchAnalysis`.
   - Then style into cards/tables.

8. **Coach’s Briefing Generation**
   - For MVP, synthesize briefing text server-side from Fastino results and Yutori context (no extra LLM needed): e.g., simple template that counts events and mentions key players.

## 11. Demo Script for Hackathon

When on stage (3 minutes):

1. **Intro (20–30s)**
   - “This is a Sports Tactics Auto‑Breakdown Assistant. Drop in a match clip; it autonomously generates highlights, tactical tags, and a coach’s briefing using Reka Vision, Fastino GLiNER‑2, and Yutori.”

2. **Setup (20s)**
   - Show a short soccer clip URL already in the form.
   - Point at an `.env` note or settings page showing the three API keys are configured.

3. **Run (60–90s)**
   - Click **Analyze Match**.
   - Talk through what’s happening:
     - “Reka Vision is generating highlight clips from the raw video.”[^1][^2]
     - “Fastino GLiNER‑2 is extracting structured events and tactics from commentary text.”[^4][^5][^6]
     - “Yutori’s Research API is fetching league and team context from the web.”[^7][^8][^9]
   - Once results load, click a couple of clips and show tags.

4. **Results (40–60s)**
   - Scroll the briefing: “Notice how it summarizes counter-attacks, set pieces, and key players.”
   - Show the Yutori context panel.

5. **Close (20s)**
   - Emphasize autonomy (one-click, runs unattended), real-world use (coaches, analysts, scouts), and extensibility (more sports, deeper ASR, richer tactics model).

## 12. Suggested Demo Match Clips

You want short, self-contained clips with clear events.

Options:

- **Football/soccer ending clip (2–3 minutes):**
  - “The Best 2 minutes of football You've Never Watched” – a D2 playoff game ending with lots of drama and commentary.[^13]
- **Tactical explanation clips (for alt/demo):**
  - “How to ANALYSE football matches | Football Tactics Explained” – 2:51 length, heavy on tactical language that GLiNER‑2 can parse.[^14]
  - “Soccer Tactics Explained: Breaking Down Tactics For Beginners” – longer but rich commentary, useful for extracting tactical patterns.[^15]

You can:

- Use one of these YouTube URLs directly as `video_urls` in Reka’s `/v1/clips` call to generate highlight clips.[^14][^13][^15][^12][^2]
- Or pre-download and host a short MP4 if you want consistent latency.

For the live demo, using a 2–3 minute YouTube clip with clear commentary (like the D2 playoff ending or the tactics explainer) will give Reka plenty to work with while keeping processing time reasonable.[^13][^15][^14][^12][^2]

***

This structure should let you implement the entire vertical slice in one focused build session: configure the three API keys, wire the single `/api/analyze` endpoint, and stand up a simple React UI to demonstrate end-to-end autonomy on a real match clip.

---

## References

1. [Vision API](https://docs.reka.ai/vision/overview) - The Reka Vision API provides powerful video processing and analysis capabilities, enabling you to up...

2. [Clip Generation API (Reka Clip)](https://docs.reka.ai/vision/highlight-clip-generation) - Documentation for Reka AI APIs.

3. [Video Q&A | Reka API](https://docs.reka.ai/vision/video-qa) - The Video Q&A API is designed for videos longer than 30 seconds. It indexes your video for efficient...

4. [GLiNER 2 Overview - Docs Template - Fastino](https://fastino.ai/docs/overview) - GLiNER 2 is Fastino's open-source, schema-based information extraction model — a unified architectur...

5. [Run Inference - Docs Template - Fastino](https://fastino.ai/api-reference/gliner-2) - Run Inference. Perform fast, schema-driven entity extraction, text classification, and structured da...

6. [Inferencing with GLiNER 2 - Docs Template - Fastino](https://fastino.ai/docs/getting-started-usage) - GLiNER 2 unifies information-extraction tasks in one efficient forward pass and is optimized for CPU...

7. [Yutori API: Overview](https://docs.yutori.com) - We offer four APIs — n1, Browsing, Research, and Scouting. The Yutori Python SDK and MCP servers are...

8. [yutori · PyPI](https://pypi.org/project/yutori/) - The official Python library and CLI for the Yutori API. Yutori provides APIs for building web agents...

9. [yutori - PyPI](https://pypi.org/project/yutori/0.1.0/) - Official Python SDK for the Yutori API

10. [Yutori Create Research Task [DB3] - MCP Tools](https://www.mcpbundles.com/tools/yutori-create-research-task-db3)

11. [Health - Yutori API](https://docs.yutori.com/reference/health)

12. [Generate AI video clips from YouTube using Reka Vision API and ...](https://n8n.io/workflows/12926-generate-ai-video-clips-from-youtube-using-reka-vision-api-and-gmail/) - Try It Out!This n8n template demonstrates how to use Reka API via HTTP to AI generate a clip automat...

13. [The Best 2 minutes of football You've Never Watched - YouTube](https://www.youtube.com/watch?v=6M8qGr_HDc0) - The Best 2 minutes of football You've Never Watched. 3.2K views · 3 years ago ...more. Isaac Punts. ...

14. [How to ANALYSE football matches | Football Tactics Explained](https://www.youtube.com/watch?v=aW2NLCrPpQk) - How do you tactically analyse a football match? Well the game is split into 4 phases; In possession,...

15. [🔥 Soccer Tactics Explained: Breaking Down Tactics For Beginners 🔥](https://www.youtube.com/watch?v=vT0uJwt4orY) - 🏆 Become a better soccer player (click here) 👉 https://bit.ly/soccerX 👈 In this video,  Soccer Tacti...

