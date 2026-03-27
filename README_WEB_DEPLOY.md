# Tap to Breathe - Browser Link Deployment

This project is now ready to deploy as a browser game link.

## What is already done

- `pygbag` web build works
- Output is created in `build/web`
- Render blueprint file is added: `render.yaml`

## Quick test locally

Build:

```bash
pygbag --build .
```

Serve the output folder:

```bash
python -m http.server 8000 --directory build/web
```

Open:

```text
http://localhost:8000
```

## Deploy on Render (shareable link)

1. Push this folder to GitHub.
2. In Render dashboard, choose **New +** -> **Blueprint**.
3. Select your GitHub repo.
4. Render reads `render.yaml` automatically.
5. Click **Apply** and wait for deploy.
6. You get a public URL like:
   `https://tap-to-breathe-web.onrender.com`

## Mobile play

- Open the Render URL on phone browser.
- Controls:
  - Tap = boost
  - Drag = move left/right

## Notes

- Browser builds may have lower FPS than native APK on older phones.
- If you want best mobile performance, keep Android APK release as primary and web link as demo/share version.
