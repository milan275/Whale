# Whale 🐋

Whale is a Python-based vault manager that lets you convert a folder into a password-protected `.whale` vault. The vault keeps your folder structure and files encrypted, so you can store sensitive data in a single secured file.

A Whale vault can also have an optional **fake password**. When the fake password is entered, Whale opens a separate fake folder instead of the real protected folder. This lets you keep decoy content available while the real vault remains protected by its own password.

> **Important:** Keep your real password safe. If it is lost, the encrypted vault cannot be recovered through Whale.

## Features

- Convert a folder into a single password-protected `.whale` vault
- Preserve nested folders and files
- Encrypt vault data using AES-GCM
- Derive encryption keys from passwords with Argon2id
- Optionally configure a fake folder and fake password
- Open and browse extracted vault contents with the Whale explorer
- Create a shortcut for convenient vault access

## Requirements

- Python 3.11 or newer
- PySide6
- cryptography

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

## Creating a Vault

Start the graphical vault builder:

```bash
python builder_gui.py
```

Complete the form:

1. **Vault Name** — the name of the vault file.
2. **Password** — the real password for the protected folder.
3. **Source Folder** — the folder to convert into a vault.
4. **Fake Folder** — an optional decoy folder.
5. **Fake Password** — the password that opens the fake folder.
6. **Vault Destination** — the directory in which the `.whale` file should be saved.

Click **Build Vault**. Whale creates a file named `<vault-name>.whale` in the selected destination.

### Fake Password Behavior

The fake vault is optional. If you provide both a fake folder and a fake password:

- Entering the **real password** opens the contents of the source folder.
- Entering the **fake password** opens the contents of the fake folder.
- The fake folder should contain harmless content that you are comfortable displaying.

The fake password is not an alternative way to recover the real vault; it is a separate password that selects the decoy content.

## Opening a Vault

Use the generated shortcut when available, or run the extraction entry point directly:

```bash
python extract.py "<vault-name>"
```

Enter either the real or fake password when prompted. The selected folder is extracted for browsing in the Whale explorer. Close the explorer when finished so its temporary extracted data can be cleaned up.

## How It Works

1. Whale generates a random salt for the vault.
2. Argon2id derives a 256-bit encryption key from the supplied password and salt.
3. The source folder structure is stored as encrypted metadata.
4. File contents are encrypted in chunks with AES-GCM.
5. The encrypted metadata and file contents are written to a `.whale` file.
6. During extraction, the password determines which vault content is opened: the real folder or the configured fake folder.

## Project Structure

```text
Whale/
├── builder_gui.py   # Graphical interface for creating vaults
├── builder.py       # Vault-building entry point
├── vault.py         # Vault creation and extraction logic
├── crypt.py         # Argon2id and AES-GCM cryptographic engine
├── extract.py       # Vault extraction entry point
├── explorer/        # Vault file browser
├── shortcut.py      # Shortcut creation utilities
├── window.py        # Reusable Qt window components
└── icons/           # Application icons
```

## Security Notes

- Use a long, unique password for the real vault.
- Do not store the real password together with the `.whale` file.
- Test a newly created vault before deleting the original source folder.
- Keep secure backups of important vault files.
- Treat extracted files as sensitive while the vault is open.
- The fake-vault feature is intended for plausible deniability and should not be treated as a substitute for full-device encryption.

## Disclaimer

Whale is provided as-is. Review and test the implementation before relying on it for highly sensitive or irreplaceable data.
