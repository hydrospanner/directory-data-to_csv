import tkinter
from tkinter.ttk import Frame, Button, Style
from tkinter.filedialog import askdirectory

from dir_info import get_csv


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
        include_files = self.include_files_chk_var.get()
        get_csv(my_path=path, max_depth=self.depth_spin.get(), include_files=include_files)
        self.status_label['text'] = 'script finished'


def main():
    root = tkinter.Tk()
    app = DirGUI(root)
    app.mainloop()

main()
