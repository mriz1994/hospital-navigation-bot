# ================================================================
#  QR CODE GENERATOR — SCUMapBot
#  شغّل الملف ده عشان تطبع أكواد QR للمستشفى
# ================================================================

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

BOT_USERNAME = "SCUMapBot"

# ── The 4 QR scan points ─────────────────────────────────────────
LOCATIONS = {
    "LOC_SHABAK":        "مدخل شباك التذاكر",
    "LOC_MAIN_GATE":     "البوابة الرئيسية",
    "LOC_EMERGENCY_GATE":"بوابة الطوارئ",
    "LOC_NEW_BUILDING":  "المبنى الجديد",
}

def make_qr(loc_id: str, arabic_name: str, output_dir: str):
    url = f"https://t.me/{BOT_USERNAME}?start={loc_id}"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_w, qr_h = qr_img.size
    label_h    = 120
    final      = Image.new("RGB", (qr_w, qr_h + label_h), "white")
    final.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final)
    try:
        font_big  = ImageFont.truetype("arial.ttf", 22)
        font_mid  = ImageFont.truetype("arial.ttf", 16)
        font_small= ImageFont.truetype("arial.ttf", 13)
    except:
        font_big = font_mid = font_small = ImageFont.load_default()

    cx = qr_w // 2
    draw.text((cx, qr_h + 10), arabic_name,         fill="black", font=font_big,   anchor="mt")
    draw.text((cx, qr_h + 45), "امسح للحصول على الاتجاهات", fill="#333333", font=font_mid,   anchor="mt")
    draw.text((cx, qr_h + 72), "Scan for Directions",       fill="#666666", font=font_small, anchor="mt")
    draw.text((cx, qr_h + 95), f"@{BOT_USERNAME}",          fill="#999999", font=font_small, anchor="mt")

    filepath = os.path.join(output_dir, f"{loc_id}.png")
    final.save(filepath, dpi=(300, 300))
    return filepath


def main():
    out = "qr_codes"
    os.makedirs(out, exist_ok=True)
    print(f"\n🔧 Generating QR codes for @{BOT_USERNAME}...\n")
    for loc_id, name in LOCATIONS.items():
        path = make_qr(loc_id, name, out)
        print(f"  ✅ {name:30s} → {path}")
    print(f"\n🎉 Done! 4 QR codes saved in '{out}/' folder")
    print("🖨️  Print each one at A5 or A4 size and laminate it")
    print("\nPlacement guide:")
    print("  LOC_SHABAK.png        → عند مدخل شباك التذاكر")
    print("  LOC_MAIN_GATE.png     → عند البوابة الرئيسية")
    print("  LOC_EMERGENCY_GATE.png→ عند بوابة الطوارئ")
    print("  LOC_NEW_BUILDING.png  → عند المبنى الجديد")


if __name__ == "__main__":
    main()
