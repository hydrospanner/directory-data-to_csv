import os
import pandas as pd
import numpy as np
import tkinter
from tkinter.ttk import Frame, Button, Style
from tkinter.filedialog import askdirectory


class DirInfo:

    def __init__(self, my_path, max_depth, include_files):
        dir_list = self.create_directory_list(my_path)
        if max_depth == 'Show all':
            max_depth = self.get_max_depth(dir_list)
        else:
            max_depth = int(max_depth)
        dir_df = self.build_df(dir_list, max_depth, my_path)
        if include_files:
            self.add_files(dir_df, dir_list, max_depth, my_path)
        dir_df.to_csv(swap_chr(swap_chr(my_path, '\\', '.'), ':', ".") + '.csv')

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except:
            return 0

    def create_directory_list(self, my_path):
        d_list = []
        for (dirpath, dirnames, filenames) in os.walk(my_path):
            file_name_size = [(file_name, self.get_size(dirpath + '\\' + file_name)) for file_name in filenames]
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
        for line in dir_list:
            depth = self.folder_depth(parent_path, line[0])
            max_depth = max(depth, max_depth)
        return max_depth

    def is_subfolder(self, path, parent_path):
        return parent_path in path

    def folder_name(self, path):
        return path.split('\\')[-1]

    def count_subfolders(self, ref_path, dir_list):
        folder_ct = 0
        for line in dir_list:
            path = line[0]
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

    def dict_to_sort_str(self, ext_dict):
        # Create sorted list of tuples with key and value of extension dictionary.
        sorted_list = sorted(ext_dict.items(), key=lambda x: x[1], reverse=True)
        # Use list comprehension to convert list of tuples to list of strings.
        return ', '.join([l[0] + '-' + str(l[1]) for l in sorted_list])

    def file_stats(self, path, dir_list):
        # Returns a tuple of the count of files in the folder and file extension string.
        file_ct = 0
        folder_size = 0
        extension_dict = {}
        for line in dir_list:
            if self.is_subfolder(line[0], path):
                folder_size += sum(file_name_size[1] for file_name_size in line[2])
                # Add the file count in this folder to the total file count.
                file_ct += len(line[2])
                # Loop through each file extension creating am extension dictionary where the value
                # is the count of files with that extension.
                for file_name in line[2]:
                    ext = self.get_extension(file_name[0])
                    if ext in extension_dict:
                        extension_dict[ext] += 1
                    else:
                        extension_dict.update({ext: 1})
        return (file_ct, self.dict_to_sort_str(extension_dict), folder_size)

    def build_df(self, dir_list, max_depth, my_path):
        # Build dataframe from folders.
        df_index = ['Full path', 'Folder/file name', 'Size, bytes', 'Subfolders', 'Files',
                    'Subfolders (including subfolders)', 'Files (including subfolders)', 'File types']
        df = pd.DataFrame(columns=df_index)
        for line in dir_list:
            path = line[0]
            f_stats = self.file_stats(path, dir_list)
            if self.folder_depth(my_path, path) <= max_depth:
                # the '.loc[len(dir_df)] =' functions as an .append() method for a dataframe.
                df.loc[len(df)] = [path,
                                   self.folder_name(path),
                                   f_stats[2],
                                   len(line[1]),
                                   len(line[2]),
                                   self.count_subfolders(path, dir_list),
                                   f_stats[0],
                                   f_stats[1]
                                   ]
        return df

    def add_files(self, dir_df, dir_list, max_depth, my_path):
        for line in dir_list:
            path = line[0]
            if self.folder_depth(my_path, path) <= max_depth:
                for file_name in line[2]:
                    dir_df.loc[len(dir_df)] = [path, file_name[0], file_name[1], '', '', '', '', '']


class DirGUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.search_folder = "Enter folder"
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Directory Info")

        Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 12')

        self.columnconfigure(0, pad=8)
        for r in range(0, 6):
            self.rowconfigure(r, pad=8)
        self.choose_dir = Button(self, text="Choose Directory", command=self.select_search_dir)
        self.choose_dir.grid(row=0, column=0)
        self.label = tkinter.ttk.Label(self, text='Choose a Directory', foreground="red", font=("Helvetica", 12))
        self.label.grid(row=1, columnspan=2)

        self.include_files_chk_var = tkinter.IntVar()
        self.include_files_chk = tkinter.Checkbutton(self, text="Include Files", font=("Helvetica", 12),
                                                     variable=self.include_files_chk_var)
        self.include_files_chk.grid(row=3, column=0)

        self.spinlabel = tkinter.ttk.Label(self, text='Select folder depth.', foreground="red",
                                           font=("Helvetica", 12))
        self.spinlabel.grid(row=2, column=0)

        spinbox_items = ['Show all']
        spinbox_items.extend(np.arange(0, 100))
        self.depth_spin = tkinter.Spinbox(self, values=spinbox_items)
        self.depth_spin.grid(row=2, column=1)

        self.run_butt = Button(self, text="Run it", command=self.run_search)
        self.run_butt.grid(row=4, column=0)

        self.status_label = tkinter.ttk.Label(self, text='', foreground="red", font=("Helvetica", 14))
        self.status_label.grid(row=5, column=0)

        self.quit = Button(self, text="QUIT", command=self.parent.destroy)
        self.quit.grid(row=4, column=1)

        self.pack()

    def select_search_dir(self):
        self.search_folder = askdirectory(initialdir="C:/",
                                          title="Choose a directory",
                                          mustexist=True)
        self.label["text"] = 'Dir: ' + self.search_folder

    def run_search(self):
        self.status_label['text'] = 'Running...'
        self.update()
        path = swap_chr(self.search_folder, '/', '\\')
        include_files = bool(self.include_files_chk_var.get())
        # Is there something I can do here to force the GUI to update?
        DirInfo(my_path=path, max_depth=self.depth_spin.get(), include_files=include_files)
        self.status_label['text'] = 'script finished'


def swap_chr(old_str, chr_old, chr_new):
    new_str = ""
    for character in old_str:
        if character == chr_old:
            new_str += chr_new
        else:
            new_str += character
    return new_str


def main():
    root = tkinter.Tk()
    app = DirGUI(root)
    app.mainloop()


main()
