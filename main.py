"""Application entry point for the Student Assessment Tracker."""


import tkinter as tk
from database import initialize_database
from interfaces.login import LoginView
from components.theme import configure_theme

def main():
    initialize_database()
    root = tk.Tk()
    configure_theme(root)
    LoginView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
