# Portfolio site

Static portfolio/landing page for the `higgsfield-pipeline` project. Plain HTML, Bootstrap 5 (CDN), and vanilla JS — no build step.

```
site/
├── index.html
├── README.md
└── assets/
    ├── style.css
    └── script.js
```

## Run locally

```bash
cd site
python -m http.server 8000
# open http://localhost:8000
```

## Deploy to Vercel

The repo root has a `vercel.json` pointing Vercel at this folder as a static output directory — no build command needed.

1. Push this repo to GitHub (already done if you're reading this on GitHub).
2. In Vercel: **New Project** → import `Lameda12/higgsfield-pipeline`.
3. Framework preset: **Other**. Leave build command empty — `vercel.json` handles the output directory.
4. Deploy.

Or via CLI:

```bash
npm i -g vercel
vercel --prod
```
