import os
import tarfile
import time
import csv
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Глобальная переменная для текущего пути в архиве
current_path = ""  # Изменено с "/" на ""

# Время запуска эмулятора для команды uptime
start_time = time.time()


# Функция для логирования команд
def log_command(command, log_file):
    with open(log_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), command])


# Функция для обработки команд
def execute_command(command, tar_path, log_file):
    global current_path, start_time
    result = ""

    with tarfile.open(tar_path, 'r') as tar:
        if command == "ls":
            # Список файлов и папок в текущей директории
            members = [member for member in tar.getmembers() if
                       member.name.startswith(current_path.lstrip('/')) and member.name != current_path]

            # Формирование списка только элементов, находящихся непосредственно в текущей папке
            unique_entries = set()
            for member in members:
                relative_path = member.name[len(current_path):].lstrip('/')
                first_part = relative_path.split('/')[0]  # Извлечение первого уровня
                unique_entries.add(first_part)

            if not unique_entries:
                result = "Directory is empty"
            else:
                result = "\n".join(sorted(unique_entries))

        elif command.startswith("cd "):
            # Переход в указанную директорию
            new_path = command.split(" ", 1)[1].strip()
            if new_path == "/":
                current_path = ""
            elif new_path == "..":
                if current_path != "":
                    current_path = "/".join(current_path.strip("/").split("/")[:-1])
                    if not current_path:
                        current_path = ""
            else:
                full_new_path = os.path.join(current_path, new_path).replace("\\", "/")

                # Проверка, существует ли такая директория в архиве
                valid_directories = set(member.name for member in tar.getmembers() if member.isdir())
                if full_new_path in valid_directories:
                    current_path = full_new_path
                else:
                    result = "No such directory"

        elif command == "pwd":
            # Вывод текущего пути
            result = current_path or "/"

        elif command == "du":
            # Размер файлов в текущей директории
            result = ""
            for member in tar.getmembers():
                if member.name.startswith(current_path) and member.name != current_path:
                    result += f"{member.name}: {member.size} bytes\n"
            if not result:
                result = "No files found."

        elif command == "uptime":
            # Время работы эмулятора
            elapsed_time = time.time() - start_time
            result = f"Uptime: {elapsed_time:.2f} seconds"

        elif command == "exit":
            # Завершение работы
            root.quit()
            result = "Exiting emulator..."

        else:
            result = f"Unknown command: {command}"

    # Логирование команды
    log_command(command, log_file)
    return result


# Функция для обработки ввода команды
def on_submit(command_entry, output_text, tar_path, log_file):
    command = command_entry.get()
    output = execute_command(command, tar_path, log_file)
    output_text.insert(tk.END, f"$ {command}\n{output}\n\n")
    command_entry.delete(0, tk.END)


# Создание интерфейса
def create_gui(tar_file_path, log_file_path):
    global root
    root = tk.Tk()
    root.title("Shell Emulator")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    output_text = tk.Text(frame, width=80, height=20, wrap=tk.WORD)
    output_text.pack(padx=5, pady=5)

    command_entry = tk.Entry(frame, width=80)
    command_entry.pack(padx=5, pady=5)

    submit_button = tk.Button(frame, text="Submit",
                              command=lambda: on_submit(command_entry, output_text, tar_file_path, log_file_path))
    submit_button.pack(pady=5)

    root.mainloop()


# Основная функция для запуска эмулятора
def run_emulator(tar_file_path, log_file_path):
    create_gui(tar_file_path, log_file_path)


# Запуск эмулятора
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python Konfigdz1.py <path_to_tar_file> <path_to_log_file>")
        sys.exit(1)

    tar_file = sys.argv[1]
    log_file = sys.argv[2]
    run_emulator(tar_file, log_file)
