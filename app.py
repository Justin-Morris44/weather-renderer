from flask import Flask, request, send_file, jsonify
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.post("/render")
def render():
    try:
        print("HIT /render", request.method, request.content_type, flush=True)

        data = request.get_json(force=True) or {}
        w = int(data.get("width", 1200))
        h = int(data.get("height", 700))
        points = data.get("points", [])

        fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=100)
        ax.set_facecolor("white")

        for p in points:
            lon = p.get("lon")
            lat = p.get("lat")

            if lon is None or lat is None:
                raise ValueError(f"Missing lat/lon in point: {p}")

            label = p.get("label", "")
            temp = p.get("temp_f", "")

            ax.text(lon, lat, f"{label}\n{temp}°",
                    ha="center", va="center", fontsize=10)

        ax.axis("off")

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype="image/png")

    except Exception as e:
        print("RENDER ERROR:", repr(e), flush=True)
        return jsonify({"ok": False, "error": str(e)}), 400
