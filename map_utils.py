"""
backend/map_utils.py
--------------------
Generates Folium maps for zone safety and route visualization.
Uses OpenStreetMap tiles (no API key needed).
"""
import folium
from folium.plugins import MarkerCluster, AntPath
import random, math

# City centers
CITY_COORDS = {
    "Delhi":     (28.6139, 77.2090),
    "Mumbai":    (19.0760, 72.8777),
    "Kolkata":   (22.5726, 88.3639),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai":   (13.0827, 80.2707),
    "Pune":      (18.5204, 73.8567),
    "Jaipur":    (26.9124, 75.7873),
}

ZONE_OFFSETS = {
    "Delhi": {
        "Connaught Place": (0.00, 0.00), "Lajpat Nagar": (-0.06, 0.08),
        "Rohini": (0.25, -0.22), "Dwarka": (-0.18, -0.28),
        "Saket": (-0.08, 0.04), "Chandni Chowk": (0.04, -0.04),
    },
    "Mumbai": {
        "Andheri": (0.18, 0.05), "Dadar": (0.04, -0.02),
        "Bandra": (0.00, 0.00), "Kurla": (0.08, 0.08),
        "Thane": (0.25, 0.20), "Colaba": (-0.20, -0.05),
    },
    "Kolkata": {
        "Park Street": (0.00, 0.00), "Salt Lake": (0.08, 0.12),
        "Howrah": (-0.02, -0.08), "Dum Dum": (0.14, 0.04),
        "Jadavpur": (-0.08, 0.06),
    },
    "Bengaluru": {
        "MG Road": (0.00, 0.00), "Koramangala": (-0.06, 0.08),
        "Whitefield": (0.04, 0.25), "Indiranagar": (0.04, 0.10),
        "Hebbal": (0.14, -0.04),
    },
    "Hyderabad": {
        "Hitech City": (0.08, -0.12), "Banjara Hills": (0.00, 0.00),
        "Secunderabad": (0.08, 0.06), "Kukatpally": (0.12, -0.08),
    },
    "Chennai": {
        "Anna Nagar": (0.08, -0.08), "T Nagar": (0.00, 0.00),
        "Velachery": (-0.10, 0.06), "Tambaram": (-0.20, 0.02),
    },
    "Pune": {
        "Shivajinagar": (0.00, 0.00), "Hadapsar": (-0.06, 0.12),
        "Kothrud": (0.02, -0.10), "Wakad": (0.10, -0.14),
    },
    "Jaipur": {
        "Pink City": (0.00, 0.00), "Vaishali Nagar": (0.04, -0.12),
        "Mansarovar": (-0.08, -0.06), "Civil Lines": (0.06, 0.02),
    },
}


def score_to_color(score):
    if score >= 65:
        return "#C9A0DC"   # lavender = safe
    elif score >= 40:
        return "#F5B8D0"   # pink = caution
    else:
        return "#FF4B6E"   # rose = danger


def make_zone_map(city, zone_df):
    """Interactive Folium map showing all zones coloured by safety score."""
    lat, lng = CITY_COORDS.get(city, (20.5937, 78.9629))
    m = folium.Map(
        location=[lat, lng], zoom_start=12,
        tiles="CartoDB dark_matter",
        attr="CartoDB"
    )

    offsets = ZONE_OFFSETS.get(city, {})
    for _, row in zone_df.iterrows():
        zone  = row["Zone"]
        score = row["Safety Score"]
        off   = offsets.get(zone, (random.uniform(-.15,.15), random.uniform(-.15,.15)))
        zlat, zlng = lat + off[0], lng + off[1]
        color = score_to_color(score)
        radius = 600 + score * 6

        # Circle overlay
        folium.Circle(
            location=[zlat, zlng], radius=radius,
            color=color, fill=True, fill_color=color, fill_opacity=0.35,
            weight=2,
        ).add_to(m)

        # Marker
        icon_html = f"""
        <div style="
            background:linear-gradient(135deg,#3D006E,#9B30D0);
            border:2px solid {color};
            border-radius:50%; width:36px; height:36px;
            display:flex; align-items:center; justify-content:center;
            font-size:11px; font-weight:700; color:{color};
            box-shadow:0 0 12px {color}88;
            font-family:sans-serif;">
          {int(score)}
        </div>"""
        folium.Marker(
            location=[zlat, zlng],
            icon=folium.DivIcon(html=icon_html, icon_size=(36, 36), icon_anchor=(18, 18)),
            popup=folium.Popup(
                f"""<div style='background:#3D006E;color:#FDFAFF;padding:10px;border-radius:8px;
                                font-family:sans-serif;font-size:13px;min-width:160px;'>
                  <b style='color:#F5B8D0'>{zone}</b><br>
                  SafeRoute Safety: <b>{score}/100</b><br>
                   Crime: {row['Crime Index']}<br>
                   Crowd: {row['Crowd Density']}/10<br>
                   Light: {row['Lighting']}/10<br>
                  <span style='color:{color};font-weight:700'>{row['Status']}</span>
                </div>""",
                max_width=220,
            ),
            tooltip=f"{zone} — {score}/100",
        ).add_to(m)

    return m


def make_route_map(city, origin_name, dest_name, routes_df):
    """Interactive map showing 3 routes with animated paths."""
    lat, lng = CITY_COORDS.get(city, (20.5937, 78.9629))

    # Generate pseudo-coordinates for origin & destination
    random.seed(hash(origin_name + dest_name) % 9999)
    olat = lat + random.uniform(-.06, .06)
    olng = lng + random.uniform(-.06, .06)
    dlat = lat + random.uniform(-.06, .06)
    dlng = lng + random.uniform(-.06, .06)

    mid_lat = (olat + dlat) / 2
    mid_lng = (olng + dlng) / 2

    m = folium.Map(
        location=[mid_lat, mid_lng], zoom_start=13,
        tiles="CartoDB dark_matter",
        attr="CartoDB"
    )

    route_colors = {
        "Route 1": "#C9A0DC",  # lavender
        "Route 2": "#F5B8D0",  # pink
        "Route 3": "#9B30D0",  # bright purple
    }

    for idx, (_, r) in enumerate(routes_df.iterrows()):
        color = route_colors.get(r["Route"], "#FDFAFF")
        score = r["Safety Score"]

        # Create a wavy path between origin and destination
        waypoints = _generate_waypoints(olat, olng, dlat, dlng, idx, score)

        # Animated dashed path
        AntPath(
            locations=waypoints,
            color=color,
            weight=4 if idx == 0 else 2.5,
            opacity=0.9 if idx == 0 else 0.55,
            delay=800,
            dash_array=[15, 25],
            pulse_color="#FDFAFF" if idx == 0 else color,
        ).add_to(m)

        # Midpoint label
        mid_idx = len(waypoints) // 2
        mlat, mlng = waypoints[mid_idx]
        label_html = f"""
        <div style="background:#3D006E;border:2px solid {color};border-radius:20px;
                    padding:3px 10px;font-size:11px;font-weight:700;color:{color};
                    font-family:sans-serif;white-space:nowrap;
                    box-shadow:0 2px 8px rgba(0,0,0,0.5);">
          {r['Route']} · {score}/100
        </div>"""
        folium.Marker(
            location=[mlat, mlng],
            icon=folium.DivIcon(html=label_html, icon_size=(120, 28), icon_anchor=(60, 14)),
            tooltip=f"{r['Route']}: {score}/100 · {r['Time (min)']} min · {r['Distance (km)']} km",
        ).add_to(m)

    # Origin marker
    folium.Marker(
        location=[olat, olng],
        icon=folium.Icon(color="purple", icon="home", prefix="fa"),
        popup=folium.Popup(f"<b style='color:#9B30D0'>{origin_name}</b>", max_width=150),
        tooltip=f" {origin_name}",
    ).add_to(m)

    # Destination marker
    folium.Marker(
        location=[dlat, dlng],
        icon=folium.Icon(color="pink", icon="flag", prefix="fa"),
        popup=folium.Popup(f"<b style='color:#F5B8D0'>{dest_name}</b>", max_width=150),
        tooltip=f" {dest_name}",
    ).add_to(m)

    return m


def _generate_waypoints(olat, olng, dlat, dlng, route_idx, score):
    """Generate slightly different curved paths for each route."""
    n = 8
    pts = []
    for i in range(n + 1):
        t = i / n
        # Linear interpolation
        clat = olat + t * (dlat - olat)
        clng = olng + t * (dlng - olng)
        # Add perpendicular offset to create curve variety
        perp_scale = 0.012 * (route_idx - 1)
        noise = math.sin(t * math.pi) * perp_scale
        # Slightly randomise based on safety score
        jitter = random.uniform(-0.003, 0.003) * (1 - score / 100)
        pts.append([clat + noise + jitter, clng - noise + jitter])
    return pts
