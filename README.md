# SafeRoute AI — Women's Safety Navigation Platform

## Project Structure

```
safe_route_ai/
├── app.py                    Entry point — Login & Sign-up pages
├── dashboard.py              Main dashboard (post-login)
├── styles.py                 Shared palette, 3D grainy background CSS, particle JS
├── requirements.txt          Python dependencies
└── backend/
    ├── __init__.py
    ├── auth.py               Register / login / SHA-256+salt hashing
    └── map_utils.py          Folium zone map + animated route map
```

### One-command launch

```bash
# Clone / download the project folder, then:
cd safe_route_ai

# App available at:
# http://localhost:8501
```
## Local 

```bash
pip install -r requirements.txt
streamlit run app.py
# Open http://localhost:8501
```
## Design System
- Background: Grainy 3D radial orb mesh (CSS) + animated particle canvas (JS)
- Fonts: Cormorant Garamond (display) + DM Sans (body)
- Palette: Deep Void #0D0018 — Purple #5B0EA6 — Bright #9B30D0 — Pink #F5B8D0 — White #FDFAFF

