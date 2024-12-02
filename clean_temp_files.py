import shutil


def clean_temp_files():
    shutil.rmtree('temp')


if __name__ == '__main__':
    clean_temp_files()
