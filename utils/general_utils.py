import os


def save_to_temp_file(text, name):
    with open(f'temp/{name}.txt', 'w', encoding='utf-8') as file:
        file.write(text)
    pass


def read_temp_file(file_name):
    if 'temp' not in file_name:
        file_path = f"temp/{file_name}.txt"
    else:
        file_path = file_name

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content

    return None