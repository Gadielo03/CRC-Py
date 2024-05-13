# CRC-Py
## CRC + Hamming Method implementation for file transfers in Python 3.12

<p align="center">
  <img src="./media/pythonLogo.png" alt="Python Logo" width="200" height="200">
</p>

### Install Python 3.12
#### Debian / Ubuntu 
```bash
$ sudo apt install python3.12
```

#### Red Hat Linux / Fedora
```bash
$ sudo dnf install python3.12
```

#### MacOs
If using brew run:
```bash
$ brew install python@3.12
```
Or install via python's .app:
<br>
[Python 3.12 for MacOS](https://www.python.org/ftp/python/3.12.3/python-3.12.3-macos11.pkg)

##### Windows
Install via python's installer:
<br>
[Pyhton 3.12 for Windows](https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe)

### Build instructions
#### Linux / MacOS
```bash
$ echo "Create the virtual environment"
$ python3.12 -m venv .venv
$ echo "Activate the virtual environment"
$ source .venv/bin/activate
$ echo "Install all dependencies"
$ pip install -r requirements.txt
```

#### Windows
```powershell
:: Create the virtual environment
python3.12 -m venv .venv 
:: Activate the virtual environment
.venv\Scripts\activate
:: Install dependencies
pip install -r requirements.txt
```
