# DeepGuard — React frontend + Django backend

The DeepGuard platform (dark landing page with live demo, analyst workspace,
admin console — 14 screens, the design you approved) as a **real React app**
(React 18 · Vite 5 · Tailwind 3 · React Router) talking to a **Django backend**
that runs the **original AdaptiveFusion model** of the MLOPS-NLP project with
the **exact output contract of the original FastAPI service** — verified
side-by-side, 29/29 checks identical (see `docs/VERIFICATION.md`).

---

## 1. Run it — two terminals

**Terminal 1 — the Django backend (model API + built UI), port 8000:**

```powershell
cd backend
pip install -r requirements.txt
python manage.py runserver
```

**Terminal 2 — the React dev server, port 5173:**

```powershell
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** — that's the platform. The Vite dev server
proxies `/predict`, `/predict/visualize`, `/health`, `/model/metadata` and
`/media` to the Django backend on port 8000, so the React app and the model
are always same-origin in the browser.

> `npm install` must be run **inside `frontend/`** (where `package.json`
> lives). If npm ever fails with `EPERM: mkdir 'E:\'`, a stray old
> `package.json` is sitting at your drive root (leftover from a previous
> extraction) — delete it and retry from the `frontend` folder.

**Single-server mode (optional).** After `npm run build` in `frontend/`, the
Django server alone serves the whole platform at
**http://127.0.0.1:8000** (SPA fallback included, like the original Colab
deployment) — no Node needed at runtime. The build output (`frontend/dist`)
ships in the zip, so this works out of the box.

### Accounts

| Role  | Email                | Password    |
|-------|----------------------|-------------|
| Admin | `admin@deepguard.io` | `Admin@2026`|
| User  | `demo@deepguard.io`  | `Demo@2026` |

Sign-up also works; new accounts get analyst access. Accounts, history and
settings live in the browser's localStorage (as in the platform prototype);
the model API itself is stateless.

---

## 2. What runs for real — verified end-to-end

- **`POST /predict`** — ONNX Runtime session, the original preprocessing
  (`resize 224 → ImageNet normalise → fftshift/fft2/log1p`) and the original
  response schema: `label`, `prob_real`, `prob_fake`, `confidence`, `logit`,
  `threshold`, `fusion_weights {spatial, frequency}` (gate softmax),
  `latency {preprocess_ms, inference_ms, total_server_ms}`,
  `model_version`, `image_size`.
- **`POST /predict/visualize`** — real Grad-CAM through PyTorch on the
  `AdaptiveFusionDetector` (feature map → gradients → ReLU-weighted CAM →
  jet overlay), PNG or JSON+base64.
- **`GET /health`**, **`GET /model/metadata`** — same fields as the original.
- The UI is wired to these endpoints. **Frontend design (two verbatim ports):**
  - `/` — the landing is the approved design from the first build (sticky
    nav, “Spot AI-generated faces…” gradient hero, browser mockup with the
    procedural face and FAKE 96.4% pill, logo strip, features, steps, live
    demo, tech card, CTA band); its live-demo tiles now run **real**
    `POST /predict` calls instead of the old simulated timer.
  - `/analyze` — the **output page of the original repo frontend**
    (`exigence_pdf/frontend`), ported verbatim: same French UI, same
    `Importer / Exemples / Webcam` tabs, `ProbabilityBars`, `FusionWeights`,
    `LatencyBadge`, `GradCamCanvas`, `ModelPanel`, `StatusBadge` components,
    same `daf-theme` light/dark toggle, wired to this Django backend. It is
    public (as in the original); signed-in users also get each analysis
    logged to their platform history.
  - `/login`, `/signup`, `/forgot` — the approved auth design (pitch panel +
    glassy form card, demo-credential chips, password meter), driving the
    platform's real account store.
  - The signed-in console (dashboard, history, admin) keeps the DeepGuard
    design system; the two systems are CSS-scoped (`.dg5` / `.daf`) and do
    not interfere.
- Error bodies, status codes and headers (`X-Process-Time-ms`,
  `X-Prediction-Label`, `X-Prob-Fake`, `X-Gradcam-Target`) match the original
  byte-for-byte — including FastAPI's automatic 422 validation body when the
  `file` field is missing.

**Weights shipped (be aware, this matters):** the trained checkpoint was
never inside the archive — the notebook's own logs say it is **125.1 MB**
(`Weights found: /content/model_output/AdaptiveFusion_best_model.pth`) and
**downloaded from Kaggle at runtime** (`weights_source="kaggle_kernel"`),
while the whole `.rar` is 16.5 MB; the repo's `.gitignore` excludes
`models/*`, `*.pth`, `*.onnx` ("versioned with DVC, never with Git") and no
DVC cache was included. So this package ships the project's own **CI dummy
weights** (`scripts/make_dummy_model.py` — same ONNX signature, same
architecture): `logit = 10 × mean(image)`, `w_spatial = sigmoid(mean(freq))`.
The whole pipeline is real, but with these weights the verdict follows image
statistics (brightness), not deepfake artefacts.

**What WAS recovered from the archive and is integrated here** — the trained
model's *reported outputs*, extracted from the training notebook's outputs in
the repo's git history (commit `afa1240`, 2026-11-18):

- `backend/reports/metrics.json` — the real evaluation results:
  **test Acc 99.79% / F1 0.9979 / AUC 1.000 / EER 0.0021** (10,000 images),
  validation **Acc 99.12% / F1 0.9913** (early stop at epoch 28), external
  cross-dataset **Acc 83.87% / AUC 0.952 / EER 0.087** (Face-VAE +
  GANsformer, 31% of fakes missed), fusion-gate statistics (fake → spatial
  0.9988, real → frequency 0.9887, 4,906 distinct gate values) and the full
  architecture parameter table (31,938,770 parameters). Served by
  `/model/metadata` and shown on the admin **Model monitoring** page.
- `backend/media/figures/` — 5 real evaluation figures: the architecture
  diagram, the test evaluation panel (confusion matrix + ROC + score
  distributions), fusion weights by class, Grad-CAM on test images, and
  qualitative results. Displayed in the admin console's
  **Training & evaluation artifacts** gallery.

**To switch every prediction to the real trained model — no code change:**

1. Copy your trained artifacts into `backend/models/`:
   - `AdaptiveFusion_best_model.pth` (the 125.1 MB `state_dict` from your
     Colab/Kaggle output — backbone auto-detected from the weights,
     `efficientnetv2_rw_s`, `convnext_tiny`, …),
   - `deepfake_fusion.onnx` (exported with `python -m src.models.onnx_export`
     from the original repo),
   - optionally `model_config.json`.
2. Optional: replace `backend/reports/metrics.json` with the output of
   `python -m src.models.evaluate` for a freshly computed card.
3. Restart `python manage.py runserver`.

---

## 3. Repository layout

```
DeepGuard_React/
├── README.md                    this file
├── docs/VERIFICATION.md         FastAPI-vs-Django proof (29/29 identical)
├── backend/                     Django project (the model service)
│   ├── manage.py
│   ├── requirements.txt         verified CPU dependency set
│   ├── .env.example             every configuration variable
│   ├── deepguard/               urls, settings, wsgi
│   ├── api/                     views (routes), inference (ONNX + Grad-CAM),
│   │                            validation (verbatim), config, middleware
│   ├── src/                     the original model package — VERBATIM
│   ├── models/                  shipped artifacts (see section 2)
│   ├── media/samples/           the 9 sample faces of the demo/workbench
│   ├── reports/                 drop your metrics.json here
│   └── scripts/make_dummy_model.py
└── frontend/                    React app (Vite + Tailwind + Router)
    ├── package.json             react 18.3, vite 5.4, tailwind 3.4
    ├── vite.config.js           dev proxy /predict /health /model /media → :8000
    ├── dist/                    prebuilt bundle (single-server mode)
    └── src/
        ├── api/client.js        the 4 endpoints + the localStorage store
        ├── App.jsx              layout, guards, health pill, notifications
        ├── components/          ui.jsx (design system), charts.jsx (SVG)
        ├── context/             Auth, Notifications, Theme, Toast
        └── pages/               public/ (Home, Login, Signup, Forgot),
                                   user/  (Dashboard, Analyze, History,
                                           Notifications, Profile),
                                   admin/ (Overview, Users, Model, Audit,
                                           Settings)
```

## 4. API reference

| Method | Path                 | Description                                   |
|--------|----------------------|-----------------------------------------------|
| GET    | `/health`            | Service + model health (503 when degraded)    |
| GET    | `/model/metadata`    | Model card, metrics, decision threshold       |
| POST   | `/predict`           | Classify a face image (multipart field `file`)|
| POST   | `/predict/visualize` | Grad-CAM overlay (`target`, `alpha`, `format`)|

```bash
curl -X POST http://127.0.0.1:8000/predict -F "file=@backend/media/samples/sample_real_1.jpg"
```

```json
{
  "label": "fake", "prob_real": 0.003, "prob_fake": 0.997,
  "confidence": 0.997, "logit": 5.71, "threshold": 0.5,
  "fusion_weights": {"spatial": 0.922, "frequency": 0.078},
  "latency": {"preprocess_ms": 9.33, "inference_ms": 0.68, "total_server_ms": 10.07},
  "model_version": "1.0.0", "image_size": [224, 224]
}
```

Errors use the original body `{"error": CODE, "detail": "...", "status_code": N}`
with 400 (invalid image), 413 (too large), 415 (unsupported type), 422
(validation), 503 (model not loaded). Accepted uploads: JPEG, PNG, WebP, BMP
up to 10 MB (`MAX_UPLOAD_MB`).

## 5. Configuration

Copy `backend/.env.example` to `backend/.env` and adjust — or keep the
defaults. `DJANGO_SECRET_KEY` and `DEBUG` follow the usual Django rules
(DEBUG=1 by default for the local demo).

## 6. Troubleshooting

**Port already in use** — `python manage.py runserver 127.0.0.1:8001`
(backend) or `npm run dev -- --port 5174` (frontend); keep both on the ports
you chose, the proxy target is in `frontend/vite.config.js`.

**"API OFFLINE" pill / demo errors** — the Django backend is not running;
start it (terminal 1) and keep the page on `http://localhost:5173`.

**Grad-CAM shows "unavailable"** — Grad-CAM needs PyTorch + the checkpoint:
`pip install torch torchvision timm` (plain `pip install torch` on Windows
gives the CPU build) and check that
`backend/models/AdaptiveFusion_best_model.pth` exists (it ships with this
package).

**First prediction / first Grad-CAM is slow** — ONNX session warm-up and
lazy PyTorch import; subsequent calls take milliseconds (watch the latency
chips, they are measured, never simulated).

**Webcam tab** — requires a camera and a secure or localhost context; frames
are analysed locally and never stored.

## 7. Differences from the original repository

- FastAPI → Django (plain views, no DRF, no database): same routes, same
  request/response contracts, same error bodies, same headers.
- The original's minimal React demo page (`exigence_pdf/frontend`) is
  replaced by the full DeepGuard platform UI (the design you approved) —
  wired to the same four endpoints.
- `src/`, `scripts/make_dummy_model.py` and `api/validation.py` are the
  original files; `api/inference.py` and `api/config.py` are the original
  logic with only the import layer adapted.
- No MLflow/DVC in this package (they belong to the training repo); drop
  `reports/metrics.json` to light up the real metrics in the admin console.
