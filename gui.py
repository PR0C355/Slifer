import tkinter as tk
import tkinter.font as font
from turtle import down

from pip import main

APP_TITLE: str = "Intice"
BLACK: str = "#191414"


root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1920x1080")
root.configure(bg=BLACK)

MAIN_MENU_FONT = font.Font(family='Spectral', size=100)
SUBTITLE_FONT = font.Font(family='Spectral', size=25)
LARGE_BUTTON_FONT = font.Font(family='Spectral', size=50)



def main_page() -> None:
    global root

    global main_title
    main_title = tk.Label(
        root,
        text = APP_TITLE,
        foreground="light gray",
        background=BLACK,
        font=MAIN_MENU_FONT
    )

    global sub_title
    sub_title = tk.Label(
        root,
        text = "An application designed for converting your favorite spotify music to an offline format.",
        foreground="light gray",
        background=BLACK,
        font=SUBTITLE_FONT
    )
    global download_button
    download_button = tk.Button(
        root,
        text = "Download",
        font = SUBTITLE_FONT,
        bg = "#63666A",
        fg = "black",
        command = remove_main_page
    )

    global spacer0
    spacer0 = tk.Label(root, "", height=10, bg=BLACK)

    main_title.pack()
    sub_title.pack()
    spacer0.pack()
    download_button.pack()

def remove_main_page() -> None:
    main_title.pack_forget()
    sub_title.pack_forget()
    spacer0.pack_forget()
    download_button.pack_forget()
    
def download_page() -> None:
    global root


main_page()
root.mainloop()