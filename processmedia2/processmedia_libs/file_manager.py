from libs.misc import file_scan


def source_file_generator(path):
    for f in file_scan(path, stats=False):
        print(f)

