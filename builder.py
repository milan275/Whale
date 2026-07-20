from vault import vault
from shortcut import Shortcut

name = input("Enter Vault name: ")
password = input("Enter password: ")
src = input("Enter path to your folder: ")
fake = input("Enter Path to your fake folder: ")

my_vault = vault(name=name,password=password,src=src,fake=fake)
my_vault.create()

s = Shortcut(r"D:\PythonEnv\Whale\extract.py", args=f'"{name}"', name=name, icon="./icons/vault_icon.ico")
s.create() 

