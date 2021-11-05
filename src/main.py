import tkinter as tk
from gui import Application

def main(): 
    root = tk.Tk()
    app = Application(root)
    root.after(10, app.show_login)
    root.mainloop()

if __name__ == '__main__':
    main()