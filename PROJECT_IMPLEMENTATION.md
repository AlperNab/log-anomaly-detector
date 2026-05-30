# Log Anomaly Detector — Standalone Real GUI Implementation

This folder is now its own runnable project app. It does not depend on the root all-project dashboard at runtime.

## Run

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default URL: `http://127.0.0.1:9134`

## What is inside this project folder

- `app/` — FastAPI backend for this project.
- `static/` — elegant browser GUI.
- `plugins/log-anomaly-detector.json` — this project’s own feature/customization/input schema.
- `project_config.json` — readable copy of the same project-specific configuration.
- `data/` — local SQLite jobs, uploads, exports.
- `tests/` — verifies this project has a registered real local engine.

## Project-specific scope

- Domain: `DevOps / Observability`
- Target user: `Domain operator, business owner, analyst, or team member who needs this workflow executed reliably.`
- Core job: Logs → anomalies and root-cause hints
- Suite: `Security Suite`

## Deep features applied

- log clustering
- anomaly scoring
- timeline correlation
- deployment correlation
- alert deduplication
- remediation hints
- runbook links

## Customization controls

- `execution_mode` — Execution mode (select)
- `log_format` — log format (select)
- `service` — service (text)
- `environment` — environment (text)
- `severity_threshold` — severity threshold (slider)
- `baseline_period` — baseline period (text)
- `noise_filters` — noise filters (text)
- `alert_channels` — alert channels (textarea)
- `output_format` — output format (select)
- `language` — language (select)
- `privacy_mode` — privacy mode (select)
- `confidence_threshold` — Confidence threshold (slider)

## Input fields

- `logs` — Logs (text) required
- `work_brief` — Work brief / source text / URL / instructions (textarea) required

## External data policy

The local deterministic core is real and executable. Live external systems are not simulated. If Shopify, ATS, ERP, OCR/STT, maps, SERP, market data, medical databases, tax/customs databases, or other live systems are required, this project reports the missing connector/API requirement instead of inventing data.

---

## Final UX/UI Layer

This project now uses the **Security Response Console** pattern.

**UX workflow:** Signal intake → severity/risk → evidence → remediation → report

**Domain components:**
- Severity matrix
- Evidence/IOC panel
- Remediation checklist
- Timeline builder
- Policy/report export

**Quick actions:**
- Triage severity
- Extract indicators
- Build remediation plan
- Prepare incident report

**No fake-data policy:** external/live actions require real connectors or API keys. Missing connectors are reported instead of simulated.
