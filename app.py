from flask import Flask, request, send_file
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.post("/render")
def render():
    data = request.get_json(force=True)
    w = int(data.get("width", 1200))
    h = int(data.get("height", 700))
    points = data.get("points", [])

    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=100)
    ax.set_facecolor("white")

    for p in points:
        lon = p["lon"]
        lat = p["lat"]
        label = p.get("label", "")
        temp = p.get("temp_f", "")
        ax.text(lon, lat, f"{label}\n{temp}°", ha="center", va="center")

    ax.axis("off")

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return send_file(buf, mimetype="image/png")
