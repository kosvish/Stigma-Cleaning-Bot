import os

# Папки, которые нужно игнорировать (чтобы не тянуть лишнее)
IGNORE_DIRS = {'.venv', '.git', '__pycache__', '.idea', '.vscode'}
OUTPUT_FILE = '../full_code.txt'


def merge_files():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # Проходим по всем папкам
        for root, dirs, files in os.walk('..'):
            # Удаляем игнорируемые папки из списка обхода
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                if file.endswith('.py') and file != 'merger.py':
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(f"\n{'=' * 50}\n")
                            outfile.write(f"FILE: {file_path}\n")
                            outfile.write(f"{'=' * 50}\n\n")
                            outfile.write(infile.read())
                            outfile.write("\n")
                    except Exception as e:
                        print(f"Ошибка чтения {file_path}: {e}")

    print(f"Готово! Весь код собран в файл {OUTPUT_FILE}")


if __name__ == '__main__':
    merge_files()