import sys, ctypes, os, threading
from vault import vault
from password import PasswordDialog

def preload():
    import explorer

if __name__ == "__main__":
    name = sys.argv[1]
    temp_root = os.path.abspath("./temp")
    temp_path = os.path.join(temp_root, name)

    if not os.path.exists(temp_root):
        os.makedirs(temp_root)
    ctypes.windll.kernel32.SetFileAttributesW(temp_root, 0x02 | 0x04)  

    loader = threading.Thread(target=preload)
    loader.start()

    pass_win = PasswordDialog()
    error = False
    while True:
        password = pass_win.get_password(error=error)
        if password is None:         
            sys.exit(0)

        my_vault = vault(name=name, password=password, ex_dest=f'./temp/{name}')
        result = my_vault.extract()  

        if result == -1:
           
            fake_name = f"fake_{name}"
            fake_whale = os.path.join("./vaults", f"{fake_name}.whale")
            if os.path.exists(fake_whale):
                fake_vault = vault(name=fake_name, password=password, ex_dest=f'./temp/{name}')
                f_result = fake_vault.extract()
                if f_result == 1:     
                    result = 0        

        if result == -1:             
            error = True
            continue
        break                        

    loader.join()
    import explorer
    app_window = explorer.window(temp_path, name)
