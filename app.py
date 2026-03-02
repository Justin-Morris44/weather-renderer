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

        # Clamp canvas size to avoid huge renders
        w = clamp(int(data.get("width", 1200)), 200, 2000)
        h = clamp(int(data.get("height", 700)), 200, 2000)
        dpi = 100

        points = data.get("points", [])
        if not isinstance(points, list):
            raise ValueError("`points` must be a list of {lat, lon, ...} objects")

        # Extract coords (accept lon or lng)
        coords = []
        for p in points:
            if not isinstance(p, dict):
                raise ValueError(f"Each point must be an object/dict. Got: {type(p)}")
            lon = p.get("lon", p.get("lng"))
            lat = p.get("lat")
            if lon is None or lat is None:
                raise ValueError(f"Missing lat/lon in point: {p}")
            coords.append((float(lon), float(lat)))

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
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype="image/png")

    except Exception as e:
        print("RENDER ERROR:", repr(e), flush=True)
        return jsonify({"ok": False, "error": str(e)}), 400
