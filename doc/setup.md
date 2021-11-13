# Setup documentation

- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Configuration](#configuration)
- [Setting up cron tasks](#setting-up-cron-tasks)
- [Setting up Hangouts notification](#setting-up-hangouts-notification)
- [Google Drive data sources](#google-drive-data-sources)
- [PBX callerid callback](#pbx-callerid-callback)

### Development setup

```bash
sudo apt-get install git gcc libffi-dev libssl-dev nodejs npm
git clone https://github.com/Som-Energia/somenergia-tomatic.git
cd somenergia-tomatic
npm install
npm run build # instead of 'deploy' for development mode assets
virtualenv .venv
python setup develop
```

### Production Setup

- Install pyenv in the running user. Follow ["Basic github install"](https://github.com/pyenv/pyenv#basic-github-checkout)

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git nodejs npm
sudo mkdir -p /opt/www/somenergia-tomatic
sudo mkdir -p /var/log/somenergia/
sudo chown tomatic:tomatic /opt/www/somenergia-tomatic
sudo su tomatic # the user that will run it

git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"
pyenv install 3.9.4 --verbose
pyenv global 3.9.4
pip install -U virtualenv
cd /opt/www/somenergia-tomatic
git clone https://github.com/Som-Energia/somenergia-tomatic.git .
virtualenv .venv
source .venv/bin/activate
python setup develop
npm install
npm run deploy # for production assets
```

### Configuration

- Copy `config-example.yaml` as `config.yaml` and edit it
- Copy `dbconfig-example.py` as `dbconfig.py` and edit it
- `echo '{}' > persons.yaml`

### Setting up cron tasks

This is needed in order to enable automations including:

- programming queues in the PBX according the turns in the timetable
- hangouts notifications just before each turn
- hangouts reporting of the daily stats
- updating the extension names in the PBX

```bash
sudo chown root:root crontab
sudo chmod 755 crontab
sudo ln -s $pwd/crontab /etc/cron.d/tomatic
```

### Setting up Hangouts notification

This can be done by using the hangups application that should have been installed as dependency.
If your main environment is still Python2, you should setup a separate Python3 virtualenv to use `hangup`.
since it is not compatible with Python 2.

- Create an account for the boot in hangouts.google.com.
- Generate an access key
  ```
  $ hangups --manual-login
  ```
  The key will be stored in `~/.cache/hangups/refresh_token.txt`
- Figure out the target channel ID. You can do so by running this hangups example:
  [`build_conversation_list.py`](https://raw.githubusercontent.com/tdryer/hangups/master/examples/build_conversation_list.py)
  which requires this other file to be in the same dir:
  [`common.py`](https://raw.githubusercontent.com/tdryer/hangups/master/examples/common.py)
- Write down channel ID in `config.yaml` as `hangoutChannel`
- You can test it by running `tomatic_says.py hello world`

### Google Drive data sources

Computing timetables requires access to a Google Drive Spreadsheet
where you store the source configuration: leaves, ideal work load...
In order to access it, you must provide a certificate.
Google change the interface so often is hard to provide a set of steps.
In overall it would be:

- Create a project in https://console.developers.google.com/project
- Create a service account within the project (service email address)
- Create a credential key within the service account (will result in a json file with a key)
- Save that file as `drive-certificate.json` in the root folder of tomatic code
- Take the `client_email` key in the json file and grant that mail access to the spreadsheet

The gspread library, this is using provide a more detailed and up to date steps:
http://gspread.readthedocs.org/en/latest/oauth2.html

If you don't want to download the configuration data from the Google Drive
SpreadSheet, you can provide the `--keep` option to the commands.

Related parameters in `config.yaml` file are:

- `documentDrive`: the title of the spreadsheet, it must be accessible by the key
- `fullCarregaIdeal`: the spreadsheet sheet where the ideal shift load is stored.
- `idealLoadValuesRange`: The range name in document and sheet with the values of the ideal load values for each person
- `idealLoadValuesName`: The range name in document and sheet with the corresponding names of each person
- `leavesSheet`: The document sheet where a person off in leave appear in every row

Holidays are taken from a sheet named as the year, pe. `2020`
containing named ranges like `Vacances202Semester1`
which are tables a column for each semester day and a row per person.

### PBX callerid callback

Tomatic can auto-search of the current incomming call.
To achieve that, you must program your PBX AGI scripts to send a request to the Tomatic API.

For example, with curl, if the person with the extension 101 is going to
receive a call from 555441234:

```bash
$ curl --max-time 1 -X POST  $BASEURL/api/info/ringring --data ext=101 --data phone=555441234 || true
```

Notice the `--max-time 1` used to avoid stalling the call if the api is down.
And notice, also, the trailing `|| true` to ensure the call success.
Both may be needed, depending on how you call this from you PBX.





