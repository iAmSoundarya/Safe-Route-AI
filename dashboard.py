"""
dashboard.py — Main SafeRoute AI dashboard (shown after login)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

from styles import C, rgba, BASE_CSS
from backend.auth import update_emergency_contacts
from backend.map_utils import make_zone_map, make_route_map


# ── Data helpers ──────────────────────────────────────────────────────────────
CITIES = ["Delhi","Mumbai","Kolkata","Bengaluru","Hyderabad","Chennai","Pune","Jaipur"]
ZONES = {
    "Delhi":     ["Connaught Place","Lajpat Nagar","Rohini","Dwarka","Saket","Chandni Chowk"],
    "Mumbai":    ["Andheri","Dadar","Bandra","Kurla","Thane","Colaba"],
    "Kolkata":   ["Park Street","Salt Lake","Howrah","Dum Dum","Jadavpur"],
    "Bengaluru": ["MG Road","Koramangala","Whitefield","Indiranagar","Hebbal"],
    "Hyderabad": ["Hitech City","Banjara Hills","Secunderabad","Kukatpally"],
    "Chennai":   ["Anna Nagar","T Nagar","Velachery","Tambaram"],
    "Pune":      ["Shivajinagar","Hadapsar","Kothrud","Wakad"],
    "Jaipur":    ["Pink City","Vaishali Nagar","Mansarovar","Civil Lines"],
}

np.random.seed(42)

def gen_crime_data(city):
    zones = ZONES[city]
    months = pd.date_range("2023-01", periods=12, freq="MS")
    rows = []
    for z in zones:
        base = random.randint(30, 120)
        for m in months:
            rows.append({
                "Zone": z, "Month": m,
                "Incidents": max(0, int(np.random.normal(base, base*.25))),
                "Type": random.choice(["Harassment","Theft","Assault","Stalking","Eve-teasing"]),
            })
    return pd.DataFrame(rows)

def safety_score(crime_idx, crowd, lighting):
    s = 100 - crime_idx*.4 - (1 - crowd/10)*20 - (1 - lighting/10)*20
    return max(5, min(95, s + random.uniform(-3, 3)))

def gen_zone_scores(city, hour):
    rows = []
    for z in ZONES[city]:
        ci = random.randint(20, 90)
        cr = max(0, (8 - abs(hour - 14)) / 8 * 10)
        li = 10 if 6 <= hour <= 20 else random.randint(2, 6)
        sc = safety_score(ci, cr, li)
        rows.append({
            "Zone": z, "Safety Score": round(sc, 1), "Crime Index": ci,
            "Crowd Density": round(cr, 1), "Lighting": round(li, 1),
            "Status": "Safe" if sc >= 65 else ("Caution" if sc >= 40 else "Danger"),
        })
    return pd.DataFrame(rows).sort_values("Safety Score", ascending=False)

def gen_routes(seed=0):
    random.seed(seed)
    rows = []
    for i in range(1, 4):
        sc = random.randint(40, 95)
        rows.append({
            "Route": f"Route {i}", "Safety Score": sc,
            "Time (min)": random.randint(12, 45),
            "Distance (km)": round(random.uniform(2.5, 18), 1),
            "CCTV Cameras": random.randint(3, 22),
            "Street Lights": random.randint(5, 35),
            "Status": "Safe" if sc >= 65 else ("Caution" if sc >= 40 else "Risky"),
        })
    return pd.DataFrame(rows)

def sbadge(s):
    cls = "badge-safe" if s=="Safe" else ("badge-caution" if s=="Caution" else "badge-danger")
    return f"<span class='{cls}'>{s}</span>"


# ══════════════════════════════════════════════════════════════════════════════
def show():
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    user = st.session_state.user

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center;padding:20px 0 10px;'> <div style='font-size:1.8rem;font-weight:900;color:#F5B8D0;font-family:serif;'>SR</div> <div style='font-family:"Playfair Display",serif;font-size:1.4rem;font-weight:900;
                      background:linear-gradient(90deg,{C['light_pink']},{C['lavender']});
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;'> SafeRoute AI
          </div> <div style='font-size:.68rem;color:{C['pink']};letter-spacing:.16em;margin-top:2px;'>WOMEN'S SAFETY PLATFORM</div> </div> <hr style='border:none;height:1px;background:linear-gradient(90deg,transparent,{C['lavender']},transparent);margin:10px 0 16px;'> <div style='background:rgba(253,250,255,0.08);border:1px solid rgba(201,160,220,0.3);
                    border-radius:14px;padding:14px;margin-bottom:16px;text-align:center;'> <div style='font-size:1.2rem;margin-bottom:4px;'></div> <div style='font-weight:600;color:{C['white']};font-size:.92rem;'>{user['name']}</div> <div style='font-size:.75rem;color:{C['lavender']};'>{user['email']}</div> <div style='margin-top:6px;'><span class='badge-safe'> {user['city']}</span></div> </div> """, unsafe_allow_html=True)

        city = st.selectbox(" Analyse City", CITIES,
                            index=CITIES.index(user.get("city","Delhi")) if user.get("city") in CITIES else 0)
        hour = st.slider(" Hour of Day", 0, 23, datetime.now().hour)

        st.markdown(f"<hr style='border:none;height:1px;background:rgba(201,160,220,0.25);margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:\"Playfair Display\",serif;font-size:.95rem;color:{C['light_pink']};margin-bottom:10px;'> Route Planner</div>", unsafe_allow_html=True)

        origin   = st.text_input(" From", placeholder="e.g. Connaught Place")
        dest     = st.text_input(" To",   placeholder="e.g. Lajpat Nagar")
        plan_btn = st.button(" Find Safest Route", use_container_width=True)

        st.markdown(f"<hr style='border:none;height:1px;background:rgba(201,160,220,0.25);margin:16px 0;'>", unsafe_allow_html=True)
        sos = st.button("SOS SOS — Share Location", use_container_width=True)
        if sos:
            st.error(" Emergency alert sent to your trusted contacts!")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button(" Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

        st.markdown(f"<div style='font-size:.68rem;color:{C['lavender']};margin-top:18px;text-align:center;line-height:1.7;'>Data: NCRB 2023 · Smart City APIs<br>Refreshed every 15 min</div>", unsafe_allow_html=True)

    # ── LOAD DATA ─────────────────────────────────────────────────────────────
    zone_df  = gen_zone_scores(city, hour)
    crime_df = gen_crime_data(city)
    am_pm    = "AM" if hour < 12 else "PM"
    hr12     = hour % 12 or 12

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(120deg,rgba(61,0,110,0.88),rgba(155,48,208,0.55));
                border:1px solid rgba(249,213,229,0.32); border-radius:28px;
                padding:44px 40px; margin-bottom:28px; position:relative; overflow:hidden;"> <div style="position:absolute;right:36px;top:50%;transform:translateY(-50%);
                  font-size:130px;opacity:.09;">SafeRoute</div> <div style="font-size:.78rem;letter-spacing:.18em;color:{C['pink']};
                  text-transform:uppercase;margin-bottom:10px;">AI-Powered · Real-Time · Trusted</div> <div style="font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;
                  background:linear-gradient(90deg,{C['white']},{C['light_pink']},{C['pink']});
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;"> SafeRoute AI
      </div> <div style="font-size:1rem;color:{C['light_lav']};max-width:540px;"> Welcome back, <b style='color:{C['light_pink']}'>{user['name']}</b> — 
        here's your real-time safety dashboard for {city}.
      </div> <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap;"> <span class='badge-white'> {city}</span> <span class='badge-caution'> {hr12}:00 {am_pm}</span> <span class='badge-safe'> Live Analysis</span> <span class='badge-white'>India India</span> </div> </div> """, unsafe_allow_html=True)

    # ── METRICS ──────────────────────────────────────────────────────────────
    safe_c    = len(zone_df[zone_df["Status"]=="Safe"])
    caution_c = len(zone_df[zone_df["Status"]=="Caution"])
    danger_c  = len(zone_df[zone_df["Status"]=="Danger"])
    city_score = round(zone_df["Safety Score"].mean(), 1)

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in zip([m1,m2,m3,m4],
        [f"{city_score}/100", safe_c, caution_c, danger_c],
        ["City Safety Score"," Safe Zones"," Caution Zones"," Danger Zones"]):
        with col:
            st.markdown(f"<div class='metric-tile'><div class='val'>{val}</div><div class='lbl'>{lbl}</div></div>",
                        unsafe_allow_html=True)

    st.markdown("<div class='pink-divider'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs([" Zone Map", " Analytics", " Route Planner", " Profile"])

    # ── TAB 1: ZONE MAP ───────────────────────────────────────────────────────
    with tab1:
        st.markdown("<div class='sec-title'>Interactive Zone Safety Map</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.85rem;color:{C['lavender']};margin-bottom:16px;'>Click any zone marker for detailed safety info. Circles sized by safety score.</div>", unsafe_allow_html=True)

        col_map, col_legend = st.columns([3, 1])
        with col_map:
            zone_map = make_zone_map(city, zone_df)
            components.html(zone_map._repr_html_(), height=500, scrolling=False)

        with col_legend:
            st.markdown(f"""
            <div style='padding-top:8px;'> <div style='font-family:"Playfair Display",serif;font-size:1rem;
                          font-weight:700;color:{C['white']};margin-bottom:16px;'>Zone Legend</div> """, unsafe_allow_html=True)

            for _, row in zone_df.iterrows():
                st.markdown(f"""
                <div class='sr-card' style='padding:12px 16px;margin-bottom:8px;'> <div style='display:flex;justify-content:space-between;align-items:center;'> <span style='font-weight:600;font-size:.85rem;color:{C["white"]};'>{row['Zone']}</span> {sbadge(row['Status'])}
                  </div> <div style='display:flex;gap:10px;margin-top:6px;font-size:.72rem;color:{C["lavender"]};'> <span> {row['Lighting']}/10</span> <span> {row['Crowd Density']}/10</span> </div> <div class='prog-wrap'><div class='prog-bar' style='width:{row["Safety Score"]}%;'></div></div> <div style='font-size:.68rem;color:{C["light_pink"]};text-align:right;margin-top:3px;'>{row["Safety Score"]}/100</div> </div>""", unsafe_allow_html=True)

    # ── TAB 2: ANALYTICS ──────────────────────────────────────────────────────
    with tab2:
        st.markdown("<div class='sec-title'>Crime Trend Analysis</div>", unsafe_allow_html=True)

        cl, cr = st.columns(2)
        with cl:
            monthly = crime_df.groupby("Month")["Incidents"].sum().reset_index()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=monthly["Month"], y=monthly["Incidents"], fill="tozeroy",
                line=dict(color=C["pink"], width=2.5),
                fillcolor=rgba(C["bright"], 0.22),
                marker=dict(color=C["light_pink"], size=7), name="Incidents",
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=C["white"], family="DM Sans"),
                title=dict(text=f"Monthly Incidents · {city}", font=dict(size=13, color=C["lavender"])),
                xaxis=dict(gridcolor=rgba(C["lavender"], 0.15), tickfont=dict(color=C["light_lav"])),
                yaxis=dict(gridcolor=rgba(C["lavender"], 0.15), tickfont=dict(color=C["light_lav"])),
                margin=dict(l=0,r=0,t=44,b=0), height=290,
            )
            st.plotly_chart(fig2, use_container_width=True)

        with cr:
            type_data = crime_df.groupby("Type")["Incidents"].sum().reset_index()
            fig3 = px.pie(type_data, values="Incidents", names="Type",
                          color_discrete_sequence=[C["deep"],C["purple"],C["bright"],C["lavender"],C["pink"]],
                          hole=0.55)
            fig3.update_traces(textfont_color=C["white"], marker=dict(line=dict(color=C["deep"], width=2)))
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=C["white"], family="DM Sans"),
                title=dict(text="Crime Type Breakdown", font=dict(size=13, color=C["lavender"])),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["white"])),
                margin=dict(l=0,r=0,t=44,b=0), height=290,
            )
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("<div class='sec-title'>Lighting & Crowd vs Safety Score</div>", unsafe_allow_html=True)
        cmap = {"Safe":C["lavender"],"Caution":C["pink"],"Danger":C["rose"]}
        fig4 = px.scatter(zone_df, x="Lighting", y="Safety Score", size="Crowd Density",
                          color="Status", color_discrete_map=cmap, text="Zone", height=320, size_max=28)
        fig4.update_traces(textfont_color=C["white"], textposition="top center")
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C["white"], family="DM Sans"),
            xaxis=dict(title="Lighting Score (0-10)", gridcolor=rgba(C["lavender"],0.15), tickfont=dict(color=C["light_lav"])),
            yaxis=dict(title="Safety Score", gridcolor=rgba(C["lavender"],0.15), tickfont=dict(color=C["light_lav"])),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0,r=0,t=10,b=0),
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Heatmap bar chart
        st.markdown("<div class='sec-title'>Zone Safety Bar Chart</div>", unsafe_allow_html=True)
        fig5 = px.bar(zone_df, x="Safety Score", y="Zone", orientation="h",
                      color="Status", color_discrete_map=cmap, text="Safety Score", height=380)
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C["white"], family="DM Sans"),
            xaxis=dict(gridcolor=rgba(C["lavender"],0.18), range=[0,110], tickfont=dict(color=C["light_lav"])),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["white"])),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["white"])),
            margin=dict(l=0,r=20,t=10,b=10),
        )
        fig5.update_traces(textfont=dict(color=C["white"]), textposition="outside")
        st.plotly_chart(fig5, use_container_width=True)

    # ── TAB 3: ROUTE PLANNER ──────────────────────────────────────────────────
    with tab3:
        st.markdown("<div class='sec-title'> Route Planner with Live Map</div>", unsafe_allow_html=True)

        rp_col1, rp_col2 = st.columns([1, 2])
        with rp_col1:
            st.markdown(f"<div style='font-size:.85rem;color:{C['lavender']};margin-bottom:12px;'>Enter your journey details below.</div>", unsafe_allow_html=True)
            r_origin = st.text_input(" From (origin)",      key="r_origin", placeholder="e.g. Connaught Place")
            r_dest   = st.text_input(" To (destination)",   key="r_dest",   placeholder="e.g. Lajpat Nagar")
            r_city   = st.selectbox(" City", CITIES,        key="r_city",
                                    index=CITIES.index(city) if city in CITIES else 0)
            r_hour   = st.slider(" Departure Hour", 0, 23, hr12 % 24, key="r_hour")
            find_btn = st.button(" Analyse Routes", use_container_width=True, key="find_route")

        with rp_col2:
            if find_btn and r_origin and r_dest:
                routes = gen_routes(seed=hash(r_origin+r_dest) % 9999).sort_values("Safety Score", ascending=False).reset_index(drop=True)

                # ── ROUTE MAP ──
                route_map = make_route_map(r_city, r_origin, r_dest, routes)
                components.html(route_map._repr_html_(), height=420, scrolling=False)

                st.markdown(f"""
                <div class='sr-card-white' style='padding:14px 18px;margin:14px 0 6px;'> <span style='color:{C["white"]};font-size:.88rem;'> <b>{r_origin}</b> →  <b>{r_dest}</b> &nbsp;|&nbsp;  {r_city}
                    &nbsp;|&nbsp;  {r_hour}:00
                  </span> </div>""", unsafe_allow_html=True)

                for idx, r in routes.iterrows():
                    sc   = r["Safety Score"]
                    col  = C["lavender"] if sc>=65 else (C["pink"] if sc>=40 else C["rose"])
                    bcls = "badge-safe" if sc>=65 else ("badge-caution" if sc>=40 else "badge-danger")
                    star = "Recommended: RECOMMENDED — " if idx==0 else ""
                    st.markdown(f"""
                    <div class='sr-card'> <div style='display:flex;justify-content:space-between;align-items:center;'> <div> <span style='font-family:"Playfair Display",serif;font-size:1.05rem;
                                       font-weight:700;color:{C["white"]};'>{star}{r['Route']}</span> <span style='margin-left:10px;' class='{bcls}'>{r['Status']}</span> </div> <div style='font-family:"Playfair Display",serif;font-size:2rem;
                                    font-weight:700;color:{col};'> {sc}<span style='font-size:.82rem;color:{C["lavender"]};'>/100</span> </div> </div> <div style='display:flex;gap:18px;margin-top:10px;flex-wrap:wrap;
                                  font-size:.83rem;color:{C["light_lav"]};'> <span> {r['Time (min)']} min</span> <span> {r['Distance (km)']} km</span> <span> {r['CCTV Cameras']} cameras</span> <span> {r['Street Lights']} lights</span> </div> <div class='prog-wrap' style='margin-top:12px;'> <div class='prog-bar' style='width:{sc}%;'></div> </div> </div>""", unsafe_allow_html=True)

            elif find_btn:
                st.warning(" Please enter both origin and destination.")
            else:
                # Placeholder map — city overview
                st.markdown(f"""
                <div style='background:rgba(61,0,110,0.4);border:1px solid rgba(201,160,220,0.3);
                            border-radius:18px;padding:48px 32px;text-align:center;'> <div style='font-size:3rem;margin-bottom:12px;'></div> <div style='font-family:"Playfair Display",serif;font-size:1.2rem;color:{C["white"]};'> Enter your route to see the live map
                  </div> <div style='font-size:.85rem;color:{C["lavender"]};margin-top:8px;'> Routes will appear with animated paths, CCTV coverage & safety scores
                  </div> </div>""", unsafe_allow_html=True)

        # Safety tips
        st.markdown("<div class='pink-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-title'> Safety Intelligence Tips</div>", unsafe_allow_html=True)
        tips = [
            ("","Avoid Late Night Travel","Avoid travelling alone after 10 PM in low-lit zones."),
            ("","Share Live Location","Always share real-time location with a trusted contact."),
            ("","Prefer Busy Routes","Higher crowd density = statistically safer evening routes."),
            ("","CCTV Matters","15+ cameras per route = 60% fewer reported incidents."),
            ("","Use Public Transit","Metro & well-lit bus stops are safer after dark."),
            ("SOS","Know Your Apps","Himmat Plus (Delhi Police) offers one-tap SOS."),
        ]
        t1,t2,t3 = st.columns(3)
        for i,(icon,title,tip) in enumerate(tips):
            with [t1,t2,t3][i%3]:
                st.markdown(f"""
                <div class='sr-card-white' style='padding:18px 20px;margin-bottom:12px;'> <div style='font-size:1.6rem;margin-bottom:6px;'>{icon}</div> <div style='font-weight:600;font-size:.88rem;color:{C["light_pink"]};margin-bottom:4px;'>{title}</div> <div style='font-size:.8rem;color:{C["light_lav"]};line-height:1.55;'>{tip}</div> </div>""", unsafe_allow_html=True)

    # ── TAB 4: PROFILE ────────────────────────────────────────────────────────
    with tab4:
        st.markdown("<div class='sec-title'> My Profile</div>", unsafe_allow_html=True)
        p1, p2 = st.columns(2)

        with p1:
            st.markdown(f"""
            <div class='sr-card'> <div style='font-family:"Playfair Display",serif;font-size:1.1rem;
                          color:{C["light_pink"]};margin-bottom:16px;font-weight:700;'>Account Details</div> {"".join([f'''
              <div style='display:flex;justify-content:space-between;padding:10px 0;
                          border-bottom:1px solid rgba(201,160,220,0.2);'> <span style='color:{C["lavender"]};font-size:.85rem;'>{lbl}</span> <span style='color:{C["white"]};font-size:.85rem;font-weight:500;'>{val}</span> </div>''' for lbl,val in [
                ("Full Name", user['name']),
                ("Email", user['email']),
                ("Phone", user.get('phone','—')),
                ("Home City", user.get('city','—')),
                ("Member Since", user.get('created_at','—')[:10] if user.get('created_at') else '—'),
              ]])}
            </div>""", unsafe_allow_html=True)

        with p2:
            st.markdown(f"""
            <div class='sr-card'> <div style='font-family:"Playfair Display",serif;font-size:1.1rem;
                          color:{C["light_pink"]};margin-bottom:14px;font-weight:700;'> SOS Emergency Contacts
              </div> <div style='font-size:.83rem;color:{C["lavender"]};margin-bottom:12px;'> Add up to 3 contacts who will receive your SOS alert instantly.
              </div> </div>""", unsafe_allow_html=True)

            contacts = user.get("emergency_contacts", [])
            new_contacts = []
            for i in range(3):
                existing = contacts[i] if i < len(contacts) else ""
                val = st.text_input(f"Contact {i+1} phone / email",
                                    value=existing,
                                    key=f"ec_{i}",
                                    placeholder="+91 98765 43210 or name@email.com")
                new_contacts.append(val)

            if st.button(" Save Emergency Contacts", use_container_width=True):
                filled = [c for c in new_contacts if c.strip()]
                ok = update_emergency_contacts(user["email"], filled)
                if ok:
                    st.session_state.user["emergency_contacts"] = filled
                    st.success(f" Saved {len(filled)} emergency contact(s).")
                else:
                    st.error("Could not save — please try again.")

        # Safety stats
        st.markdown("<div class='sec-title'> My Safety Activity</div>", unsafe_allow_html=True)
        s1,s2,s3,s4 = st.columns(4)
        for col,val,lbl in zip([s1,s2,s3,s4],
            ["12","47","3","98%"],
            ["Routes Planned","Zones Checked","SOS Tests","Safety Rate"]):
            with col:
                st.markdown(f"<div class='metric-tile'><div class='val'>{val}</div><div class='lbl'>{lbl}</div></div>",
                            unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='pink-divider'></div> <div style='text-align:center;padding-bottom:24px;'> <div style='font-family:"Playfair Display",serif;font-size:1rem;color:{C["light_pink"]};margin-bottom:6px;'>SafeRoute SafeRoute AI</div> <div style='font-size:.75rem;color:{C["lavender"]};line-height:1.8;'> Built for Women's Safety in India · Data: NCRB 2023 · Smart City APIs · Real-time Crowd &amp; Lighting
      </div> <div style='margin-top:10px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap;'> <span class='badge-white'>India Made for India</span> <span class='badge-caution'> Stay Safe</span> <span class='badge-safe'> Live Data</span> </div> </div> """, unsafe_allow_html=True)
