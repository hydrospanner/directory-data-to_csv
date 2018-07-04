import os
import pandas as pd


def get_csv(my_path, max_depth, include_files):
    dir_list = create_directory_list(my_path)
    if max_depth == 'Show all':
        max_depth = get_max_depth(dir_list)
    else:
        max_depth = int(max_depth)
    dir_df = build_df(dir_list, max_depth, my_path)
    if include_files:
        dir_df = add_files(dir_df, dir_list, max_depth, my_path)
    out_file_name = my_path.replace('\\', '.').replace(':', '.') + '.csv'
    column_order = ['Full path', 'Folder/file name', 'Size, bytes', 'Subfolders', 'Files',
                    'Subfolders (including subfolders)', 'Files SF', 'File types']
    dir_df = dir_df[column_order]
    dir_df.to_csv(os.path.join('data out', out_file_name), index=False)


def get_size(path):
    try:
        return os.path.getsize(path)
    except PermissionError:
        return 0


def create_directory_list(my_path):
    d_list = []
    for dirpath, dirnames, filenames in os.walk(my_path):
        file_name_size = [(file_name, get_size(os.path.join(dirpath, file_name))) for file_name in filenames]
        d_list.append((dirpath, dirnames, file_name_size))
    return d_list


def folder_depth(parent_path, lookup_path):
    # Return how many folders down a subfolder is relative to the parent folder.
    return lookup_path.count('\\') - parent_path.count('\\')


def get_max_depth(dir_list):
    # Maximum folder depth in directory.
    max_depth = 0
    parent_path = dir_list[0][0]
    for path, _, _ in dir_list:
        depth = folder_depth(parent_path, path)
        max_depth = max(depth, max_depth)
    return max_depth


def is_subfolder(path, parent_path):
    return parent_path in path


def folder_name(path):
    return path.split('\\')[-1]


def count_subfolders(ref_path, dir_list):
    folder_ct = 0
    for path, _, _ in dir_list:
        if is_subfolder(path, ref_path):
            folder_ct += 1
    # Subtract 1 to not count the base folder.
    return folder_ct - 1


def get_extension(file_name):
    # Return file extension of file name. Not case sensitive.
    if '.' in file_name:
        return file_name.split('.')[-1].lower()
    else:
        return 'unknown'


def file_names_to_val_cts(file_names, extension_dict):
    for file_name in file_names:
        ext = get_extension(file_name)
        if ext in extension_dict:
            extension_dict[ext] += 1
        else:
            extension_dict[ext] = 1
    return extension_dict


def dict_to_sort_str(ext_dict):
    # Create sorted list of tuples with key and value of extension dictionary.
    sorted_list = sorted(ext_dict.items(), key=lambda x: x[1], reverse=True)
    # Use list comprehension to convert list of tuples to list of strings.
    return ', '.join(['-'.join([ext, str(count)]) for ext, count in sorted_list])


def file_stats(in_path, dir_list):
    # Returns a tuple of the count of files in the folder and file extension string.
    file_ct = 0
    folder_size = 0
    extension_dict = {}
    for path, dir_names, file_name_size in dir_list:
        if is_subfolder(path, in_path):
            folder_size += sum(size for name, size in file_name_size)
            # Add the file count in this folder to the total file count.
            file_ct += len(file_name_size)
            file_names = [file_name for file_name, _ in file_name_size]
            extension_dict = file_names_to_val_cts(file_names, extension_dict)
    return file_ct, dict_to_sort_str(extension_dict), folder_size


def build_base_df(dir_list):
    base = []
    for path, dir_names, file_name_size in dir_list:
        base.append((path, folder_name(path), len(dir_names), len(file_name_size)))
    return pd.DataFrame(base, columns=['Full path', 'Folder/file name', 'Subfolders', 'Files'])


def build_df(dir_list, max_depth, my_path):
    # Build dataframe from folders.
    df = build_base_df(dir_list)
    df['depth'] = df['Full path'].apply(lambda x: folder_depth(my_path, x))
    df = df[df['depth'] <= max_depth].copy()
    df['Subfolders (including subfolders)'] = df['Full path'].apply(lambda p: count_subfolders(p, dir_list))
    df['Files SF'], df['File types'], df['Size, bytes'] = (
        zip(*df['Full path'].apply(lambda x: file_stats(x, dir_list)))
    )
    return df


def add_files(dir_df, dir_list, max_depth, my_path):
    l = []
    for path, dir_names, file_name_size in dir_list:
        if folder_depth(my_path, path) <= max_depth:
            for file_name, file_size in file_name_size:
                l.append([path, file_name, file_size])
    file_df = pd.DataFrame(l, columns=['Full path', 'Folder/file name', 'Size, bytes'])
    return dir_df.append(file_df)
