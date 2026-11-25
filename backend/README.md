# Backend — the model service

Django port of the original FastAPI backend (same routes, same contracts,
same error bodies — see `../docs/VERIFICATION.md`). Run:

```powershell
pip install -r requirements.txt
python manage.py runserver
```

Endpoints: `GET /health`, `GET /model/metadata`, `POST /predict`,
`POST /predict/visualize` (see `../README.md` for the full reference).
Model artifacts live in `models/`; drop your trained checkpoint there to
replace the shipped CI dummy weights. Full project documentation:
`../README.md`.
