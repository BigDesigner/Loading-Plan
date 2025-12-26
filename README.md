# Akansu Loading Plan – PDF Generator

This repository contains a lightweight web app used to generate a **Loading Plan** PDF for scheduled shipments.

## Features
- Simple web form (Customer Name, Queue No, Product Type, Loading Date, Loading Time Slot)
- Generates a clean, single‑page PDF
- Includes a small header logo (`static/logo.png`)
- Time slot is limited to two predefined options:
  - 08:00–12:00
  - 13:00–16:00
- Basic protection: PDF generation requires an access code (default: `akansu`)

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open: http://localhost:5000

## Deploy (Render)
This repo includes `render.yaml`. When creating a new service on Render, connect the repository and deploy.

### Change the access code
Set an environment variable:
- `PDF_PASSWORD` (default is `akansu`)

## Notes
This project is intentionally small and easy to maintain. You can customize the PDF layout, fields, and wording as needed.
