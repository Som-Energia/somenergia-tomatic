# somenergia-phonetimetable

Repartidor d'hores d'atenció telefònica


## Dependencies


```bash
sudo apt-get install gcc libpython2.7-dev libffi-dev libssl-dev
pip install PyYaml
pip install gspread
pip install oauth2client
pip install PyOpenSSL
```

## Usage

To download availability information from google drive:

```bash
$ ./schedulehours.py get
```

See bellow how to grant access to the script.

To compute the timetable:

```bash
$ ./schedulehours.py
```

## Deployment

In order to access the configuration available in the Google Drive SpreadSheet
you must provide a 

- Create a Google Apps credential:
    - Create a project in https://console.developers.google.com/project
    - Go to “Credentials” and hit “Create new Client ID”.
    - Select “Service account”. Hitting “Create Client ID” will generate a new
      Public/Private key pair.
    - Download and save it as 'credential.json' in the same folder the script is
    - Take the `client_email` key in the json file and grant it access to the
      'Vacances' file as it was a google user

If you don't want to download the configuration data from the Google Drive
SpreadSheet, you can provide the `--keep` option.


## Certificates

Unless you specify the `--keep` option, required configuration data is
downloaded from the Google Drive spreadsheet where phone load, holidays and
availability are written down.

In order to access it you will require a oauth2 certificate and to grant it
access to the Document.

Follow instructions in http://gspread.readthedocs.org/en/latest/oauth2.html

You can skip steps 5 (already in installation section in this document) and
step 6 (code related) but **don't skip step 7**.

Create a link named 'certificate.json' pointing to the actual certificate.



