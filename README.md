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



## Certificates

The `--down` downloads required configuration data from the drive file
where phone load, holidays and availability are written down.

In order to access it you will require a oauth2 certificate and to grant it access.

Follow instructions in http://gspread.readthedocs.org/en/latest/oauth2.html

You can skip steps 5 (already in installation section in this document) and step 6 (code related)
but **don't skip step 7**.

Create a link named 'certificate.json' pointing to the actual certificate.



