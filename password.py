import tkinter as tk

class PasswordDialog:
    def __init__(self, title="Enter Password"):
        self.title = title
        self.password = None

    def get_password(self, error=False):
        root = tk.Tk()
        root.title(self.title)
        root.geometry("300x150")
        root.resizable(False, False)

        label = tk.Label(root, text="Enter Vault Password:")
        label.pack(pady=(12, 4))

        # error message label — only visible when error=True
        err_lbl = tk.Label(root, text="Wrong Password!" if error else "",
                           fg="#cc3333", font=("", 9, "bold"))
        err_lbl.pack()

        entry = tk.Entry(root, show="*", width=30)
        entry.pack(pady=5)
        entry.focus()

        def submit(event=None):
            self.password = entry.get()
            root.destroy()

        entry.bind("<Return>", submit)

        btn = tk.Button(root, text="Submit", command=submit, width=10)
        btn.pack(pady=8)

        root.mainloop()
        return self.password


if __name__ == "__main__":
    dialog = PasswordDialog()
    pwd = dialog.get_password()
    print(f"Captured Password: {pwd}")