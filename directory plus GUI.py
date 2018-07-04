import os
import pandas as pd
import tkinter
from tkinter.ttk import Frame, Button, Style
from tkinter.filedialog import askdirectory
import datetime


class DirInfo:

    def __init__(self, my_path, max_depth, include_files):
        start_time = datetime.datetime.now()
        dir_list = self.create_directory_list(my_path)
        self.dir_list_time = datetime.datetime.now()
        print('create dir_list', (self.dir_list_time - start_time).seconds)
        if max_depth == 'Show all':
            max_depth = self.get_max_depth(dir_list)
        else:
            max_depth = int(max_depth)
        dir_df = self.build_df(dir_list, max_depth, my_path)
        if include_files:
            dir_df = self.add_files(dir_df, dir_list, max_depth, my_path)
        out_file_name = my_path.replace('\\', '.').replace(':', '.') + '.csv'
        column_order = ['Full path', 'Folder/file name', 'Size, bytes', 'Subfolders', 'Files',
                        'Subfolders (including subfolders)', 'Files SF', 'File types']
        dir_df = dir_df[column_order]
        dir_df.to_csv(out_file_name, index=False)

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except PermissionError:
            return 0

    def create_directory_list(self, my_path):
        d_list = []
        for dirpath, dirnames, filenames in os.walk(my_path):
            file_name_size = [(file_name, self.get_size(os.path.join(dirpath, file_name))) for file_name in filenames]
            d_list.append((dirpath, dirnames, file_name_size))
        return d_list

    def folder_depth(self, parent_path, lookup_path):
        # Return how many folders down a subfolder is relative to the parent folder.
        # Use count method of string to return occurrence of specific character in string.
        return lookup_path.count('\\') - parent_path.count('\\')

    def get_max_depth(self, dir_list):
        # Maximum folder depth in directory.
        max_depth = 0
        parent_path = dir_list[0][0]
        for path, _, _ in dir_list:
            depth = self.folder_depth(parent_path, path)
            max_depth = max(depth, max_depth)
        return max_depth

    def is_subfolder(self, path, parent_path):
        return parent_path in path

    def folder_name(self, path):
        return path.split('\\')[-1]

    def count_subfolders(self, ref_path, dir_list):
        folder_ct = 0
        for path, _, _ in dir_list:
            if self.is_subfolder(path, ref_path):
                folder_ct += 1
        # Subtract 1 to not count the base folder.
        return folder_ct - 1

    def get_extension(self, file_name):
        # Return file extension of file name. Not case sensitive.
        if '.' in file_name:
            return file_name.split('.')[-1].lower()
        else:
            return 'unknown'

    def file_names_to_val_cts(self, file_names, extension_dict):
        for file_name in file_names:
            ext = self.get_extension(file_name)
            if ext in extension_dict:
                extension_dict[ext] += 1
            else:
                extension_dict[ext] = 1
        return extension_dict

    def dict_to_sort_str(self, ext_dict):
        # Create sorted list of tuples with key and value of extension dictionary.
        sorted_list = sorted(ext_dict.items(), key=lambda x: x[1], reverse=True)
        # Use list comprehension to convert list of tuples to list of strings.
        return ', '.join(['-'.join([ext, str(count)]) for ext, count in sorted_list])
        # return ', '.join([ext + '-' + str(count) for ext, count in sorted_list])

    def value_count_str(self, l):
        s = pd.Series(l)
        return ', '.join(['-'.join([k, str(v)]) for k, v in s.value_counts()[:5].iteritems()])

    def file_stats(self, in_path, dir_list):
        # Returns a tuple of the count of files in the folder and file extension string.
        file_ct = 0
        folder_size = 0
        extension_dict = {}
        for path, dir_names, file_name_size in dir_list:
            if self.is_subfolder(path, in_path):
                folder_size += sum(size for name, size in file_name_size)
                # Add the file count in this folder to the total file count.
                file_ct += len(file_name_size)
                file_names = [file_name for file_name, _ in file_name_size]
                extension_dict = self.file_names_to_val_cts(file_names, extension_dict)
                # extensions = self.value_count_str([self.get_extension(file_name) for file_name, _ in file_name_size])
        return file_ct, self.dict_to_sort_str(extension_dict), folder_size

    def build_base_df(self, dir_list):
        base = []
        for path, dir_names, file_name_size in dir_list:
            base.append((path, self.folder_name(path), len(dir_names), len(file_name_size)))
        return pd.DataFrame(base, columns=['Full path', 'Folder/file name', 'Subfolders', 'Files'])

    def build_df(self, dir_list, max_depth, my_path):
        # Build dataframe from folders.
        df = self.build_base_df(dir_list)
        df['depth'] = df['Full path'].apply(lambda x: self.folder_depth(my_path, x))
        df = df[df['depth'] <= max_depth].copy()
        df['Subfolders (including subfolders)'] = df['Full path'].apply(lambda p: self.count_subfolders(p, dir_list))
        subfolder_created_time = datetime.datetime.now()
        print('subfolders counted', (subfolder_created_time - self.dir_list_time).seconds)
        df['Files SF'], df['File types'], df['Size, bytes'] = zip(*df['Full path'].apply(lambda x:
                                                                                         self.file_stats(x, dir_list)))
        stats_time = datetime.datetime.now()
        print('stats', (stats_time - subfolder_created_time).seconds)
        return df

    def add_files(self, dir_df, dir_list, max_depth, my_path):
        l = []
        for path, dir_names, file_name_size in dir_list:
            if self.folder_depth(my_path, path) <= max_depth:
                for file_name, file_size in file_name_size:
                    l.append([path, file_name, file_size])
        file_df = pd.DataFrame(l, columns=['Full path', 'Folder/file name', 'Size, bytes'])
        return dir_df.append(file_df)


class DirGUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.search_folder = "Enter folder"
        self.parent = parent
        self.parent.title("Directory Info")
        self.initUI()

    def initUI(self):
        Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 12')
        self.columnconfigure(0, pad=8)
        for r in range(0, 6):
            self.rowconfigure(r, pad=8)

        choose_dir = Button(self, text="Choose Directory", command=self.select_search_dir)
        choose_dir.grid(row=0, column=0)
        self.label = tkinter.ttk.Label(self, text='Choose a Directory', foreground="red", font=("Helvetica", 12))
        self.label.grid(row=1, columnspan=2)

        self.include_files_chk_var = tkinter.IntVar()
        include_files_chk = tkinter.Checkbutton(self, text="Include Files", font=("Helvetica", 12),
                                                variable=self.include_files_chk_var)
        include_files_chk.grid(row=3, column=0)

        spinlabel = tkinter.ttk.Label(self, text='Select folder depth.', foreground="red",
                                           font=("Helvetica", 12))
        spinlabel.grid(row=2, column=0)

        spinbox_items = ['Show all']
        spinbox_items.extend([n for n in range(99)])
        self.depth_spin = tkinter.Spinbox(self, values=spinbox_items)
        self.depth_spin.grid(row=2, column=1)

        run_butt = Button(self, text="Run it", command=self.run_search)
        run_butt.grid(row=4, column=0)

        self.status_label = tkinter.ttk.Label(self, text='', foreground="red", font=("Helvetica", 14))
        self.status_label.grid(row=5, column=0)

        quit_button = Button(self, text="QUIT", command=self.parent.destroy)
        quit_button.grid(row=4, column=1)

        self.pack()

    def select_search_dir(self):
        self.search_folder = askdirectory(initialdir="C:/",
                                          title="Choose a directory",
                                          mustexist=True)
        self.label["text"] = 'Dir: ' + self.search_folder

    def run_search(self):
        self.status_label['text'] = 'Running...'
        self.update()
        path = self.search_folder.replace('/', '\\')
        include_files = bool(self.include_files_chk_var.get())
        DirInfo(my_path=path, max_depth=self.depth_spin.get(), include_files=include_files)
        self.status_label['text'] = 'script finished'


def main():
    root = tkinter.Tk()
    app = DirGUI(root)
    app.mainloop()

main()
