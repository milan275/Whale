import sys, ctypes, os, threading
from vault import vault
from password import PasswordDialog

def preload_libraries():
    import explorer

if __name__ == "__main__":
    name = sys.argv[1]
    temp_root = os.path.abspath("./temp")
    temp_path = os.path.join(temp_root, name)

    if not os.path.exists(temp_root):
        os.makedirs(temp_root)
    ctypes.windll.kernel32.SetFileAttributesW(temp_root, 0x02 | 0x04)

    loader_thread = threading.Thread(target=preload_libraries)
    loader_thread.start()

    pass_win = PasswordDialog()
    password = pass_win.get_password()

    my_vault = vault(name=name, password=password,ex_dest=f'./temp/{name}')
    fake = not my_vault.extract()

    loader_thread.join()
    import explorer
    app_window = explorer.window(temp_path, name)