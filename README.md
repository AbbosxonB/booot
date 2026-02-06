# Universitet uchun Telegram Service Desk Bot — System Analysis va Product Architecture

Ushbu hujjat universitet talabalarining murojaatlarini qabul qilish, to‘g‘ri bo‘limlarga avtomatik yo‘naltirish va admin/xodimlar uchun qulay boshqaruv tizimini yaratish bo‘yicha **to‘liq konsept va funksional arxitektura**ni taqdim etadi.

## 1. Maqsad va qiymat (Product Goals)

- **Talabalar murojaatlari javobsiz qolmasligi**
- **Murojaatlarning noto‘g‘ri bo‘limlarga tushishini oldini olish**
- **Xodimlar uchun tez, sodda va tartibli ish jarayoni**
- **Ticket-boshqaruv asosida service desk tizimi**

## 2. Foydalanuvchi rollari va ruxsatlar

| Rol | Imkoniyatlar |
| --- | --- |
| **Talaba** | Murojaat yuboradi, holatini ko‘radi, FAQ ko‘radi, e’lonlarni o‘qiydi, profilini boshqaradi |
| **Xodim** | Faqat o‘z bo‘limiga tushgan ticketlarga javob beradi |
| **Admin** | Barcha murojaatlarni ko‘radi, e’lon yuboradi, statistikani ko‘radi |
| **Superadmin** | Xodimlar, bo‘limlar, ruxsatlar va konfiguratsiyani boshqaradi |

## 3. Talaba uchun asosiy bot menyusi (UX)

- 📌 **Ma’lumotlar (FAQ)**
- 📨 **Murojaat yuborish**
- 📄 **Murojaatlarim**
- 👤 **Profil**
- 📢 **E’lonlar**

> **Muhim:** Talaba bo‘lim nomlarini ko‘rmaydi. Bot savol–javob orqali bo‘limni **o‘zi aniqlaydi**.

## 4. Murojaat (ticket) ishlov berish logikasi

### 4.1. Bosqichlar

1. Talaba **muammo turini** tanlaydi
2. Talaba **sub-mavzuni** tanlaydi
3. Bot **bo‘limni avtomatik aniqlaydi**
4. Kerakli savollar beriladi (minimal maydonlar)
5. Ticket yaratiladi

### 4.2. Ticket holatlari

- **OPEN** — yangi tushgan murojaat
- **IN_PROGRESS** — xodim ishlamoqda
- **ANSWERED** — javob berilgan
- **CLOSED** — talaba tasdiqlasa yoki SLA tugagach yopiladi

### 4.3. SLA va monitoring

- **1 talaba → ma’lum vaqt ichida 1 ticket** (spamga qarshi)
- **Deadline eslatmalari** (xodim va admin uchun)
- **Javobsiz ticketlar admin paneliga chiqadi**
- **Ticket javobsiz yopilmaydi**

## 5. Bo‘limlar va sub-mavzular (final mapping)

### 5.1. DEKANAT — (Akademik + Hujjat)
**Yo‘nalish:** Talabaning statusi va akademik huquqlari

Sub-mavzular:
- Chaqiruv qog‘ozi
- Ma’lumotnoma (o‘qish joyidan)
- Transkript (ochirish / yoqish)
- Bahoga e’tiroz **(prioritet yuqori)**
- Boshqa (izoh bilan)

### 5.2. O‘QUV BO‘LIMI — (Tashkiliy)
**Yo‘nalish:** O‘quv jarayonini tashkil etish

Sub-mavzular:
- Dars jadvali
- Fanlar ro‘yxati
- O‘qituvchi almashishi
- Auditoriya masalalari
- O‘quv reja
- Boshqa

### 5.3. BUXGALTERIYA — (Hisob-kitob)
**Yo‘nalish:** Pul harakati va hisob

Sub-mavzular:
- To‘lovlar bo‘yicha qarzdorlik
- To‘lov kvitansiyasi
- Stipendiya
- Hisob-kitob xatolari
- To‘lovni qaytarish
- Boshqa

> “Pul qayerga ketdi?” → **Buxgalteriya**

### 5.4. MARKETING — (Kontrakt)
**Yo‘nalish:** Shartnoma va majburiyatlar

Sub-mavzular:
- Kontrakt summasi
- Kontrakt nusxasi
- To‘lov muddati
- To‘lov kvitansiyasi
- Boshqa

> “Qancha va qachon to‘layman?” → **Marketing**

### 5.5. IT — (Axborot texnologiyalari)
**Yo‘nalish:** Tizim va texnik muammolar

Sub-mavzular:
- Login / parol
- Portal ishlamasligi
- Telegram bot xatosi
- Boshqa

> Ticket ochilishidan oldin **FAQ tekshiriladi**.

## 6. Ma’lumot so‘rash qoidalari

- Har bir sub-mavzu uchun **faqat kerakli maydonlar**
- Ortiqcha savol yo‘q
- **“Boshqa”** sub-mavzuda **majburiy izoh**

## 7. Admin / Xodim paneli funksiyalari

- 📥 **Yangi murojaatlar**
- 🕒 **Javobsiz murojaatlar**
- 🔁 **O‘tkazish (bo‘lim/xodim)**
- 📢 **E’lon yuborish**
- 📊 **Statistika**

### Ruxsatlar

- **Xodim** → faqat o‘z bo‘limi
- **Admin** → barcha bo‘limlar
- **Superadmin** → sozlamalar, xodimlar, bo‘limlar

## 8. Saqlanadigan ma’lumotlar (Data Model)

- Foydalanuvchilar (rol, guruh)
- Ticketlar
- Xabarlar tarixi
- Holatlar
- Bo‘limlar
- Xodimlar

## 9. Tavsiya etiladigan arxitektura (High-Level)

**Bot + Admin Panel + Backend API + DB** ko‘rinishida modul arxitektura:

- **Telegram Bot** → talabalar va xodimlar interfeysi
- **Admin Panel (Web)** → admin/superadmin boshqaruvi
- **Backend API** → routing, SLA, permission checks
- **DB** → ticketlar, foydalanuvchilar, loglar

## 10. Kengaytirilish va yuklama

- **Kengaytiriladigan** modul struktura
- **Yuklamaga bardoshli** (queue/worker bilan)
- **Real universitet jarayonlariga mos** (SLA, eskalatsiya, ruxsatlar)

---

Agar keyingi bosqich sifatida **ma’lumotlar bazasi modeli**, **API endpointlar**, yoki **xodimlar uchun workflow diagram** kerak bo‘lsa, alohida specification tayyorlanadi.
