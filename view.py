import tkinter
from tkinter import messagebox, simpledialog

CLOSING_PROTOCOL = "WM_DELETE_WINDOW"
END_OF_LINE = "\n"
KEY_RETURN = "<Return>"
TEXT_STATE_DISABLED = "disabled"
TEXT_STATE_NORMAL = "normal"

CONNECTION_ERROR = "Could not connect to server"
ERROR = "Error"
INPUT_SERVER_HOST = "Input Server Host"
INPUT_SERVER_PORT = "Input Server Port"
INPUT_USERNAME = "Input your username"
SEND = "Send"
SERVER_HOST = "Server Host"
SERVER_PORT = "Server Port"
# TITLE = "ezChat"
USERNAME = "Username"


class BlindSearchGameUI(object):
    def __init__(self, client):
        self.client = client
        self.gui = None
        self.frame = None
        self.input_field = None
        self.message = None
        self.message_list = None
        self.scrollbar = None
        self.send_button = None

    def show(self):
        self.gui = tkinter.Tk()
        # self.gui.title(TITLE)
        self.fill_frame()
        self.gui.protocol(CLOSING_PROTOCOL, self.on_closing)
        # return self.input_dialogs()
        return True

    def loop(self):
        self.gui.mainloop()

    def fill_frame(self):
        self.frame = tkinter.Frame(self.gui)
        self.scrollbar = tkinter.Scrollbar(self.frame)
        self.message_list = tkinter.Text(self.frame, state=TEXT_STATE_DISABLED)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.message = tkinter.IntVar()
        self.frame.pack()
        self.input_field = tkinter.Entry(self.gui, textvariable=self.message)
        self.input_field.pack()
        self.input_field.bind(KEY_RETURN, self.client.send)
        self.send_button = tkinter.Button(self.gui, text=SEND, command=self.client.send)
        self.send_button.pack()

    def input_dialogs(self):
        self.gui.lower()
        # self.client.username = simpledialog.askstring(USERNAME, INPUT_USERNAME, parent=self.gui).lower()
        if self.client.username is None:
            return False
        self.gui.title(self.client.username.upper())
        return True

    def alert(self, title, message):
        messagebox.showerror(title, message)

    def show_message(self, message):
        self.message_list.configure(state=TEXT_STATE_NORMAL)
        self.message_list.insert(tkinter.END, str(message) + END_OF_LINE)
        self.message_list.configure(state=TEXT_STATE_DISABLED)

    def on_closing(self):
        self.client.exit()
        self.gui.destroy()
