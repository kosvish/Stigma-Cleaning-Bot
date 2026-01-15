import sqlite3

DB_NAME = "db.sqlite3"


def migrate():
    print(f"🔄 Начинаю миграцию {DB_NAME}...")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # SQL команда для добавления колонки
        cursor.execute("ALTER TABLE users ADD COLUMN platrum_id TEXT")

        conn.commit()
        print("✅ Колонка 'platrum_id' успешно добавлена!")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("⚠️ Колонка уже существует, миграция не требуется.")
        else:
            print(f"❌ Ошибка SQL: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()