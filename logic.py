import sqlite3

DB_NAME = "career_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            audience TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
            user_id INTEGER PRIMARY KEY,
            audience TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM professions")
    if cursor.fetchone() == 0:
        demo_data = [
            ("Разработчик игр", "it", "teen", "Создает миры и логику видеоигр. Подходит, если ты любишь математику, логику и гейминг."),
            ("2D/3D Художник", "design", "teen", "Рисует персонажей и локации для игр и анимации. Нужен навык рисования."),
            ("SMM-специалист", "marketing", "teen", "Ведет и развивает соцсети брендов. Отличный старт для общительных ребят."),
            ("Лидер проектов (Scrum-мастер)", "management", "teen", "Организует работу команды. Подходит для тех, кто умеет объединять людей."),

            ("Специалист по Кибербезопасности", "it", "adult", "Защищает данные компаний от хакеров. Огромный спрос на рынке, высокая оплата."),
            ("UX/UI Дизайнер", "design", "adult", "Проектирует удобные интерфейсы сайтов и приложений. Ценится прошлый жизненный опыт."),
            ("Интернет-маркетолог", "marketing", "adult", "Настраивает рекламу и привлекает клиентов. Подходит для тех, кто любит аналитику."),
            ("Прожект-менеджер (PM)", "management", "adult", "Управляет бюджетами, сроками и командами. Идеально для людей с руководящим прошлым.")
        ]
        cursor.executemany(
            "INSERT INTO professions (title, category, audience, description) VALUES (?, ?, ?, ?)", 
            demo_data
        )
        conn.commit()
    conn.close()

def save_user_audience(user_id, audience):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_states (user_id, audience) VALUES (?, ?)", (user_id, audience))
    conn.commit()
    conn.close()

def get_user_audience(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT audience FROM user_states WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_profession(audience, category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM professions WHERE audience = ? AND category = ? LIMIT 1", (audience, category))
    result = cursor.fetchone()
    conn.close()
    return result
