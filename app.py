"""
SafeRoute AI — Main entry point
Handles Login / Sign-up routing then loads the dashboard.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="SafeRoute AI · Women's Safety",
    page_icon="SafeRoute",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from styles import BASE_CSS, C
from backend.auth import register_user, login_user

st.markdown(BASE_CSS, unsafe_allow_html=True)

# ── session defaults ──────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"   # "login" | "signup"

# ── if logged in → go to dashboard ───────────────────────────────────────────
if st.session_state.authenticated:
    import dashboard
    dashboard.show()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ══════════════════════════════════════════════════════════════════════════════

# Full-page hero split layout
left_col, right_col = st.columns([1, 1], gap="large")

# ── LEFT — brand panel ────────────────────────────────────────────────────────
with left_col:
    st.markdown(f"""
    <div style="min-height:92vh; display:flex; flex-direction:column;
                justify-content:center; padding:48px 32px;"> <div style="font-size:.8rem; letter-spacing:.22em; color:{C['pink']};
                  text-transform:uppercase; margin-bottom:16px;"> AI — Women's Safety — India
      </div> <div style="font-family:'Playfair Display',serif; font-size:3.8rem;
                  font-weight:900; line-height:1.1; margin-bottom:20px;
                  background:linear-gradient(135deg,{C['white']},{C['light_pink']},{C['pink']});
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;"> Navigate<br>India Safely.
      </div> <div style="font-size:1.05rem; color:{C['light_lav']}; line-height:1.7;
                  max-width:400px; margin-bottom:32px;"> Real-time safety intelligence powered by crime data,
        crowd density &amp; street lighting — so every woman
        can move freely &amp; fearlessly.
      </div> <div style="display:flex; flex-direction:column; gap:14px; max-width:340px;"> {"".join([f'''
        <div style="display:flex; align-items:center; gap:14px;
                    background:rgba(253,250,255,0.07); border:1px solid rgba(201,160,220,0.3);
                    border-radius:14px; padding:14px 18px;"> <span style="font-size:1.5rem;">{icon}</span> <div> <div style="font-weight:600; font-size:.9rem; color:{C['white']};">{title}</div> <div style="font-size:.78rem; color:{C['lavender']};">{desc}</div> </div> </div>''' for icon, title, desc in [
          ("", "Smart Route Planning", "3 ranked safe routes with live scoring"),
          ("", "Live Crime Heatmaps", "Zone-by-zone safety analysis"),
          ("SOS", "One-tap SOS", "Instant alert to your emergency contacts"),
          ("", "Lighting & Crowd Intel", "Know what's on your path before you go"),
        ]])}
      </div> <div style="margin-top:36px; display:flex; gap:10px; flex-wrap:wrap;"> <span class="badge-safe">India 8 Cities</span> <span class="badge-caution"> NCRB 2023 Data</span> <span class="badge-white"> Secure & Private</span> </div> </div> """, unsafe_allow_html=True)

# ── RIGHT — auth form ─────────────────────────────────────────────────────────
with right_col:
    st.markdown(f"""
    <div style="min-height:92vh; display:flex; align-items:center;
                justify-content:center; padding:32px 16px;"> """, unsafe_allow_html=True)

    # Tab switch buttons
    tab_l, tab_r = st.columns(2)
    with tab_l:
        if st.button("Log In", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()
    with tab_r:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    if st.session_state.auth_page == "login":
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:24px;"> <div style="font-size:2.4rem;">SafeRoute</div> <div style="font-family:'Playfair Display',serif; font-size:1.8rem;
                      font-weight:700; color:{C['white']};">Welcome Back</div> <div style="font-size:.85rem; color:{C['lavender']}; margin-top:4px;"> Log in to your SafeRoute account
          </div> </div> """, unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input(" Email address", placeholder="you@example.com")
            password = st.text_input(" Password", type="password", placeholder="Your password")
            submitted = st.form_submit_button("Log In →", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                result = login_user(email, password)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.user = result["user"]
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])

        st.markdown(f"""
        <div style="text-align:center; margin-top:18px; font-size:.84rem; color:{C['lavender']};"> Don't have an account?
          <span style="color:{C['pink']}; cursor:pointer;" 
                onclick="window.location.reload()">Sign up for free</span> </div> <div style="text-align:center; margin-top:28px;"> <div style="font-size:.72rem; color:{C['lavender']}; opacity:.6;"> Your data is encrypted and never shared
          </div> </div> """, unsafe_allow_html=True)

        # Demo shortcut
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        if st.button(" Try Demo Account", use_container_width=True):
            # Auto-register demo if not present, then login
            register_user("Demo User", "demo@saferoute.ai", "9999999999", "demo1234", "Delhi")
            res = login_user("demo@saferoute.ai", "demo1234")
            st.session_state.authenticated = True
            st.session_state.user = res["user"]
            st.rerun()

    # ── SIGN UP ───────────────────────────────────────────────────────────────
    else:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:22px;"> <div style="font-size:2.2rem;"></div> <div style="font-family:'Playfair Display',serif; font-size:1.8rem;
                      font-weight:700; color:{C['white']};">Create Account</div> <div style="font-size:.85rem; color:{C['lavender']}; margin-top:4px;"> Join thousands of women navigating safely
          </div> </div> """, unsafe_allow_html=True)

        CITIES = ["Delhi","Mumbai","Kolkata","Bengaluru","Hyderabad","Chennai","Pune","Jaipur"]

        with st.form("signup_form"):
            name     = st.text_input(" Full Name",     placeholder="Priya Sharma")
            email    = st.text_input(" Email",         placeholder="you@example.com")
            phone    = st.text_input(" Phone Number",  placeholder="+91 98765 43210")
            city     = st.selectbox(" Home City", CITIES)
            password = st.text_input(" Password",      type="password", placeholder="Min 6 characters")
            confirm  = st.text_input(" Confirm Password", type="password", placeholder="Repeat password")
            agree    = st.checkbox("I agree to the Terms of Service & Privacy Policy")
            submitted = st.form_submit_button("Create My Account →", use_container_width=True)

        if submitted:
            if not all([name, email, phone, password, confirm]):
                st.error("Please fill in all fields.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not agree:
                st.warning("Please agree to the Terms of Service.")
            else:
                result = register_user(name, email, phone, password, city)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.user = result["user"]
                    st.success(f" Welcome to SafeRoute AI, {name}!")
                    st.rerun()
                else:
                    st.error(result["message"])

    st.markdown("</div>", unsafe_allow_html=True)
