"""Shared color palette and CSS for SafeRoute AI"""

C = {
    "deep":       "#3D006E",
    "purple":     "#6A0DAD",
    "bright":     "#9B30D0",
    "lavender":   "#C9A0DC",
    "light_lav":  "#E2CBF0",
    "pink":       "#F5B8D0",
    "light_pink": "#F9D5E5",
    "white":      "#FDFAFF",
    "rose":       "#FF4B6E",
}

def rgba(hex6, alpha):
    h = hex6.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


BASE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {{
    --deep:{C['deep']}; --purple:{C['purple']}; --bright:{C['bright']};
    --lavender:{C['lavender']}; --light-lav:{C['light_lav']};
    --pink:{C['pink']}; --light-pink:{C['light_pink']}; --white:{C['white']};
}}

html,body,[data-testid="stAppViewContainer"] {{
    background:linear-gradient(135deg,{C['deep']} 0%,{C['purple']} 45%,{C['bright']} 100%) !important;
    font-family:'DM Sans',sans-serif !important;
    color:{C['white']} !important;
}}
[data-testid="stHeader"] {{ background:transparent !important; }}
[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{C['deep']}EE 0%,{C['purple']}CC 100%) !important;
    border-right:2px solid rgba(201,160,220,0.3) !important;
}}
[data-testid="stSidebar"] * {{ color:{C['white']} !important; }}

.sr-card {{
    background:linear-gradient(135deg,rgba(155,48,208,0.28),rgba(106,13,173,0.18));
    border:1px solid rgba(201,160,220,0.4); border-radius:20px; padding:22px 26px;
    backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(61,0,110,0.5);
    margin-bottom:14px; transition:transform .2s,box-shadow .2s;
}}
.sr-card:hover {{ transform:translateY(-3px); box-shadow:0 16px 40px rgba(61,0,110,0.75); }}

.sr-card-white {{
    background:linear-gradient(135deg,rgba(253,250,255,0.12),rgba(249,213,229,0.10));
    border:1px solid rgba(253,250,255,0.28); border-radius:20px; padding:22px 26px;
    backdrop-filter:blur(14px); box-shadow:0 6px 24px rgba(61,0,110,0.4); margin-bottom:14px;
}}

.auth-card {{
    background:linear-gradient(160deg,rgba(61,0,110,0.92),rgba(106,13,173,0.80));
    border:1px solid rgba(249,213,229,0.30); border-radius:28px; padding:44px 40px;
    backdrop-filter:blur(20px); box-shadow:0 20px 60px rgba(0,0,0,0.5);
    max-width:480px; margin:0 auto;
}}

.badge-safe    {{ background:rgba(201,160,220,0.20); border:1px solid {C['lavender']}; border-radius:50px; padding:4px 16px; font-size:.82rem; color:{C['lavender']}; display:inline-block; }}
.badge-caution {{ background:rgba(245,184,208,0.18); border:1px solid {C['pink']};    border-radius:50px; padding:4px 16px; font-size:.82rem; color:{C['pink']};    display:inline-block; }}
.badge-danger  {{ background:rgba(255,75,110,0.18);  border:1px solid {C['rose']};    border-radius:50px; padding:4px 16px; font-size:.82rem; color:#FF8BA7;         display:inline-block; }}
.badge-white   {{ background:rgba(253,250,255,0.15); border:1px solid rgba(253,250,255,0.45); border-radius:50px; padding:4px 16px; font-size:.82rem; color:{C['white']}; display:inline-block; }}

.metric-tile {{
    background:linear-gradient(135deg,rgba(253,250,255,0.12),rgba(245,184,208,0.10));
    border:1px solid rgba(253,250,255,0.22); border-radius:18px; padding:24px 16px; text-align:center;
}}
.metric-tile .val {{ font-family:'Playfair Display',serif; font-size:2.5rem; font-weight:700; color:{C['light_pink']}; line-height:1; }}
.metric-tile .lbl {{ font-size:.78rem; color:{C['lavender']}; text-transform:uppercase; letter-spacing:.12em; margin-top:6px; }}

.sec-title {{
    font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700;
    color:{C['white']}; margin:36px 0 18px; border-left:4px solid {C['pink']}; padding-left:14px;
}}
.prog-wrap {{ margin-top:10px; background:rgba(61,0,110,0.6); border-radius:8px; height:7px; }}
.prog-bar  {{ height:7px; border-radius:8px; background:linear-gradient(90deg,{C['bright']},{C['pink']},{C['light_pink']}); }}
.pink-divider {{ height:2px; background:linear-gradient(90deg,transparent,{C['pink']},{C['lavender']},transparent); border:none; margin:36px 0; }}

.stButton>button {{
    background:linear-gradient(135deg,{C['bright']},{C['purple']}) !important;
    color:{C['white']} !important; border:none !important; border-radius:50px !important;
    font-family:'DM Sans',sans-serif !important; font-weight:600 !important; font-size:.95rem !important;
    padding:10px 28px !important;
    box-shadow:0 4px 18px rgba(155,48,208,0.45) !important; transition:all .2s !important;
}}
.stButton>button:hover {{ transform:scale(1.04) !important; box-shadow:0 8px 28px rgba(155,48,208,0.7) !important; }}

.stTextInput>div>div>input,
.stSelectbox>div>div {{
    background:rgba(61,0,110,0.6) !important;
    border:1px solid rgba(201,160,220,0.45) !important;
    border-radius:12px !important; color:{C['white']} !important;
}}
.stTextInput>label, .stSelectbox>label {{ color:{C['lavender']} !important; font-size:.85rem !important; }}
</style>
"""
