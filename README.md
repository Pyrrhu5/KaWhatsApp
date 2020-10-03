# KaWhatsApp

Use Selenium and Google translate to automatically translate messages in WhatsApp which are in Georgian alphabet.

## Installation

Only tested on Linux.

**Python**

Python version 3.6 or above

```bash
python3 --version
```

**Clone the repository**

Git is required
```bash
git --version
```

Clone it
```bash
git clone https://aymericdeschard@bitbucket.org/aymericdeschard/kawhatsapp.git
```

**Virtual env**

Optional, but `Run.sh` assumes you have setup a virtual env as such:

```bash
python3 -m venv venv
```

**Dependencies**

Activate the virtual env first:
```bash
source ./venv/bin/activate
```

Install dependencies:

```bash
pip3 install -r requirements.txt
```

**Executable**

Allows execution of entry point (not needed for Windows)
```bash
chmod +x KaWhatsapp.py
```
or, if using the virtual env
```bash
chmod +x Run.sh
```

## Update

```bash
git pull
```


## License
Unmodified [MIT license](https://opensource.org/licenses/MIT)

See `License.md`
