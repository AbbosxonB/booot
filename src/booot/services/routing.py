from booot.enums import Priority

# Student bo‘lim nomlarini ko‘rmaydi — shu “subtopic -> department” mapping ichkarida qoladi.

DEPARTMENTS = [
    ("DEKANAT", "Dekanat"),
    ("OQUV", "O‘quv bo‘limi"),
    ("BUX", "Buxgalteriya"),
    ("MKT", "Marketing (Kontrakt)"),
    ("IT", "IT bo‘limi"),
]

SUBTOPICS = [
    # DEKANAT
    ("DEKANAT_CALLUP", "Chaqiruv qog‘ozi", "DEKANAT", Priority.NORMAL, "comment"),
    ("DEKANAT_CERT", "Ma’lumotnoma (o‘qish joyidan)", "DEKANAT", Priority.NORMAL, "comment"),
    ("DEKANAT_TRANSCRIPT", "Transkript (ochirish / yoqish)", "DEKANAT", Priority.NORMAL, "comment"),
    ("DEKANAT_GRADE_APPEAL", "Bahoga e’tiroz", "DEKANAT", Priority.HIGH, "subject,comment"),
    ("DEKANAT_OTHER", "Boshqa (izoh bilan)", "DEKANAT", Priority.NORMAL, "comment_required"),

    # O‘QUV
    ("OQUV_SCHEDULE", "Dars jadvali", "OQUV", Priority.NORMAL, "comment"),
    ("OQUV_COURSE_LIST", "Fanlar ro‘yxati", "OQUV", Priority.NORMAL, "comment"),
    ("OQUV_TEACHER_CHANGE", "O‘qituvchi almashishi", "OQUV", Priority.NORMAL, "comment"),
    ("OQUV_ROOM", "Auditoriya masalalari", "OQUV", Priority.NORMAL, "comment"),
    ("OQUV_PLAN", "O‘quv reja", "OQUV", Priority.NORMAL, "comment"),
    ("OQUV_OTHER", "Boshqa", "OQUV", Priority.NORMAL, "comment"),

    # BUX
    ("BUX_DEBT", "To‘lovlar bo‘yicha qarzdorlik", "BUX", Priority.NORMAL, "comment"),
    ("BUX_RECEIPT", "To‘lov kvitansiyasi", "BUX", Priority.NORMAL, "comment"),
    ("BUX_STIPEND", "Stipendiya", "BUX", Priority.NORMAL, "comment"),
    ("BUX_ERRORS", "Hisob-kitob xatolari", "BUX", Priority.NORMAL, "comment"),
    ("BUX_REFUND", "To‘lovni qaytarish", "BUX", Priority.NORMAL, "comment"),
    ("BUX_OTHER", "Boshqa", "BUX", Priority.NORMAL, "comment"),

    # MKT
    ("MKT_SUM", "Kontrakt summasi", "MKT", Priority.NORMAL, "comment"),
    ("MKT_COPY", "Kontrakt nusxasi", "MKT", Priority.NORMAL, "comment"),
    ("MKT_DEADLINE", "To‘lov muddati", "MKT", Priority.NORMAL, "comment"),
    ("MKT_RECEIPT", "To‘lov kvitansiyasi", "MKT", Priority.NORMAL, "comment"),
    ("MKT_OTHER", "Boshqa", "MKT", Priority.NORMAL, "comment"),

    # IT (FAQ check before ticket in handler)
    ("IT_LOGIN", "Login / parol", "IT", Priority.NORMAL, "comment"),
    ("IT_PORTAL", "Portal ishlamasligi", "IT", Priority.NORMAL, "comment"),
    ("IT_BOT", "Telegram bot xatosi", "IT", Priority.NORMAL, "comment"),
    ("IT_OTHER", "Boshqa", "IT", Priority.NORMAL, "comment"),
]
