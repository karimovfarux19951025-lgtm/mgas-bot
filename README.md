# 🌿 MGAS Telegram Bot

**Toza makon – toza kelajak!**

Chiqindi bilan bog'liq murojaatlarni qabul qiluvchi va boshqaruvchi Telegram bot.

---

## 📁 Fayl tuzilmasi

```
mgas_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── database.py         # Ma'lumotlar bazasi
├── requirements.txt    # Kutubxonalar
└── handlers/
    ├── user.py         # Foydalanuvchi handlerlar
    └── admin.py        # Admin handlerlar
```

---

## ⚙️ O'rnatish

### 1. Python o'rnating (3.10+)

### 2. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 3. `config.py` ni sozlang

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # @BotFather dan oling
ADMIN_IDS = [123456789]             # Sizning Telegram ID ingiz
```

> **Telegram ID ni qanday bilaman?**
> @userinfobot ga `/start` yuboring — u sizning ID ingizni ko'rsatadi.

### 4. Botni ishga tushiring
```bash
python bot.py
```

---

## 🤖 Bot funksiyalari

### 👤 Foydalanuvchi uchun:
| Tugma | Vazifa |
|-------|--------|
| 📝 Murojaat yuborish | Yangi murojaat yaratish |
| 📋 Mening murojaatlarim | Barcha murojaatlar holati |
| ℹ️ Yordam | Qo'llanma |

**Murojaat yuborish jarayoni:**
1. Muammo turini tanlang (6 tur mavjud)
2. Lokatsiya yuboring yoki manzilni yozing
3. Izoh yozing (ixtiyoriy)
4. Rasm yuboring (ixtiyoriy)

### 👮 Admin uchun:
| Buyruq/Tugma | Vazifa |
|-------------|--------|
| `/admin` | Admin panelni ochish |
| 📊 Statistika | Umumiy hisobot |
| 🆕 Yangi murojaatlar | Ko'rib chiqilmagan murojaatlar |
| ⏳ Jarayondagi | Ish olib borilayotganlar |
| ✔️ Bajarilganlar | Yopilgan murojaatlar |

**Murojaat holatlari:**
- 🆕 Yangi
- ✅ Qabul qilindi
- ⏳ Jarayonda
- ✔️ Bajarildi
- ❌ Rad etildi

---

## 📊 Ma'lumotlar bazasi

SQLite ishlatiladi (`mgas.db` fayli avtomatik yaratiladi).

**Jadvallar:**
- `users` — foydalanuvchilar
- `complaints` — murojaatlar

---

## 🚀 Server (VPS) da ishga tushirish

```bash
# Screen yoki systemd ishlatish tavsiya etiladi
screen -S mgas_bot
python bot.py
# Ctrl+A, D — background da qoldirish
```

Yoki `systemd` service yarating:
```ini
[Unit]
Description=MGAS Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/mgas_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
