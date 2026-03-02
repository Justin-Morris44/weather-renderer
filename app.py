from flask import Flask, request, send_file, jsonify
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)

def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))

@app.post("/render")
def render():
    try:
        print("HIT /render", request.method, request.content_type, flush=True)

        data = request.get_json(force=True) or {}

        # HARD clamp so output can never exceed safe limits
        w = clamp(int(data.get("width", 1200)), 200, 1400)
        h = clamp(int(data.get("height", 700)), 200, 900)
        dpi = 100

        points = data.get("points", [])
        if not isinstance(points, list):
            raise ValueError("`points` must be a list of {lat, lon, ...} objects")

        # Validate + collect coords (accept lon or lng)
        coords = []
        for p in points:
            if not isinstance(p, dict):
                raise ValueError(f"Each point must be an object/dict. Got: {type(p)}")
            lon = p.get("lon", p.get("lng"))
            lat = p.get("lat")
            if lon is None or lat is None:
                raise ValueError(f"Missing lat/lon in point: {p}")
            coords.append((float(lon), float(lat)))

        print("RENDER SIZE (w,h,dpi) =", w, h, dpi, "points=", len(coords), flush=True)

        fig, ax = plt.subplots(figsize=(w / dpi, h / dpi), dpi=dpi)
        ax.set_facecolor("white")

        # Auto-zoom to fit points with padding
        if coords:
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            pad_lon = max(0.2, (max(lons) - min(lons)) * 0.15)
            pad_lat = max(0.2, (max(lats) - min(lats)) * 0.15)
            ax.set_xlim(min(lons) - pad_lon, max(lons) + pad_lon)
            ax.set_ylim(min(lats) - pad_lat, max(lats) + pad_lat)

        # Draw points
        for p in points:
            lon = float(p.get("lon", p.get("lng")))
            lat = float(p.get("lat"))
            label = str(p.get("label", "")).strip()
            temp = p.get("temp_f", "")
            temp_str = "" if temp == "" else str(temp)

            text = f"{label}\n{temp_str}°".strip()
            ax.text(lon, lat, text, ha="center", va="center", fontsize=10)

        ax.axis("off")

        buf = BytesIO()

        # IMPORTANT: DO NOT use bbox_inches="tight" (can create massive pixel dimensions)
        plt.savefig(buf, format="png")
        plt.close(fig)

        buf.seek(0)
        return send_file(buf, mimetype="image/png")

    except Exception as e:
        print("RENDER ERROR:", repr(e), flush=True)
        return jsonify({"ok": False, "error": str(e)}), 400
