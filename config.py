import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

ADMIN_IDS = [6080141947]

COMPLAINT_TYPES = {
    "chiqindi_olinmagan": "🗑 Chiqindi olinmagan",
    "nogoniy_chiqindi": "♻️ Noto'g'ri chiqindi",
    "konteyner_togan": "🚮 Konteyner to'lgan",
    "texnika_muammosi": "🚛 Texnika muammosi",
    "xodim_muammosi": "👷 Xodim muammosi",
    "boshqa": "📋 Boshqa muammo",
}

STATUSES = {
    "yangi": "🆕 Yangi",
    "qabul_qilindi": "✅ Qabul qilindi",
    "jarayonda": "⏳ Jarayonda",
    "bajarildi": "✔️ Bajarildi",
    "rad_etildi": "❌ Rad etildi",
}
