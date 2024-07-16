import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from algorithm.algorithm import algorithm

class GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("поиск космических тел")
        self.root.geometry('400x100')
        self.root['background'] = "gray"
        self.root.resizable(False, False)
    
        self.my_font = ("Arial", 16) 
        self.style_frame = ttk.Style()
        self.style_frame.configure("CustomFrame.TFrame", background="white")
        self.style_Entry = ttk.Style()
        self.style_Entry.configure("TEntry", padding=5, font=self.my_font, foreground="black", background="gray")
        self.style_label = ttk.Style()
        self.style_label.configure("TLabel", font=self.my_font, padding=10, foreground="white", background="gray")
    
        self.main_menu = tk.Menu()
        self.main_menu.add_cascade(label="найти объекты", command=lambda directory: algorithm(directory))
        self.main_menu.add_cascade(label="сохранить параметры", command = self.safe_parametres)
    
        self.input_label = ttk.Label(self.root, style="TLabel", text="Введите название директории")
        self.input_label.pack()
        self.input_Entry = ttk.Entry(self.root, justify="center", width=30, style="TEntry")
        self.input_Entry.pack()
        
        self.root.config(menu=self.main_menu)
        
        self.directory = None
        
    def start(self) -> None:
        self.root.mainloop()
        
    def safe_parametres(self) -> None:
        directory = self.input_Entry.get()
        showinfo(title="успешно", message="данные сохранены")