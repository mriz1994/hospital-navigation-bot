# ================================================================
#  QR CODE GENERATOR — SCUMapBot — 9 scan points
# ================================================================

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

BOT_USERNAME = "SCUMapBot"

LOCATIONS = {
    "LOC_SHABAK":               "مدخل شباك التذاكر",
    "LOC_MAIN_GATE":            "البوابة الرئيسية",
    "LOC_EMERGENCY_GATE":       "بوابة الطوارئ",
    "LOC_NEW_BUILDING":         "المبنى الجديد",
    "LOC_HESABAT":              "قسم الحسابات",
    "LOC_COMPLEX_INSIDE":       "داخل مجمع العيادات",
    "LOC_COMPLEX_EXIT":         "مخرج المجمع — جنب الأشعة",
    "LOC_AMALIYAT_ENTRANCE":    "مدخل العمليات",
    "LOC_MAIN_BUILDING_INSIDE": "داخل المبنى الرئيسي",
    "LOC_STAFF_REGISTRATION":   "مكتب تسجيل العاملين",
}

PLACEMENT = {
    "LOC_SHABAK":               "على الحيطة عند مدخل شباك التذاكر",
    "LOC_MAIN_GATE":            "على الحيطة عند البوابة الرئيسية",
    "LOC_EMERGENCY_GATE":       "على الحيطة عند بوابة الطوارئ",
    "LOC_NEW_BUILDING":         "على واجهة المبنى الجديد",
    "LOC_HESABAT":              "على حيطة قسم الحسابات المطلة على الطريق",
    "LOC_COMPLEX_INSIDE":       "على الحيطة عند مدخل مجمع العيادات من الداخل",
    "LOC_COMPLEX_EXIT":         "على الحيطة عند مخرج المجمع جنب الأشعة",
    "LOC_AMALIYAT_ENTRANCE":    "على الحيطة جنب ضابط الأمن عند مدخل العمليات",
    "LOC_MAIN_BUILDING_INSIDE": "على الحيطة جوه المبنى الرئيسي عند المدخل",
    "LOC_STAFF_REGISTRATION":   "على الحيطة عند مكتب تسجيل العاملين",
}

def make_qr(loc_id, arabic_name, output_dir):
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
    label_h = 130
    final   = Image.new("RGB", (qr_w, qr_h + label_h), "white")
    final.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final)
    try:
        font_big   = ImageFont.truetype("arial.ttf", 22)
        font_mid   = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 13)
    except:
        font_big = font_mid = font_small = ImageFont.load_default()

    cx = qr_w // 2
    draw.line([(20, qr_h + 5), (qr_w - 20, qr_h + 5)], fill="#cccccc", width=1)
    draw.text((cx, qr_h + 15), arabic_name,                fill="black",   font=font_big,   anchor="mt")
    draw.text((cx, qr_h + 50), "امسح للحصول على الاتجاهات", fill="#222222", font=font_mid,   anchor="mt")
    draw.text((cx, qr_h + 78), "Scan for Directions",       fill="#555555", font=font_small, anchor="mt")
    draw.text((cx, qr_h + 100),"@SCUMapBot",                fill="#888888", font=font_small, anchor="mt")

    filepath = os.path.join(output_dir, f"{loc_id}.png")
    final.save(filepath, dpi=(300, 300))
    return filepath


def main():
    out = "qr_codes"
    os.makedirs(out, exist_ok=True)
    print(f"\n🔧 Generating {len(LOCATIONS)} QR codes for @{BOT_USERNAME}...\n")

    for loc_id, name in LOCATIONS.items():
        path      = make_qr(loc_id, name, out)
        placement = PLACEMENT.get(loc_id, "")
        print(f"  ✅ {name:35s} → {os.path.basename(path)}")
        print(f"     📌 يتحط: {placement}\n")

    print("=" * 60)
    print(f"🎉 تم! {len(LOCATIONS)} أكواد QR اتحفظوا في مجلد 'qr_codes/'")
    print("🖨️  اطبع كل واحد A4 أو A5 وسيّل بالبلاستيك")
    print("=" * 60)


if __name__ == "__main__":
    main()
