# Tomàtic Setup Documentation

- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Configuration](#configuration)
- [Setting up cron tasks](#setting-up-cron-tasks)
- [Setting up Hangouts notification](#setting-up-hangouts-notification)
- [PBX callerid callback](#pbx-callerid-callback)

### Development setup

```bash
sudo apt-get install git gcc libffi-dev libssl-dev nodejs npm libyaml-dev
git clone https://github.com/Som-Energia/somenergia-tomatic.git
cd somenergia-tomatic
npm install
npm run build # instead of 'deploy' for development mode assets
python --version # before create the .venv make sure the python version is 3.9.4
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### Using Makefile

It is also possible to install front and back dependencies and start the project using make:

```bash
make ui-deps # to install ui dependencies
make api-deps # to install the backend dependencies

# and then to run the project, in different terminals, as both should be kept running
make ui-dev
make api-dev
```

See Tomàtic interface on `http://localhost:4555/`

### Production Setup

- Install pyenv in the running user. Follow ["Basic github install"](https://github.com/pyenv/pyenv#basic-github-checkout)

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git nodejs npm
sudo mkdir -p /opt/www/somenergia-tomatic
sudo mkdir -p /var/log/somenergia/
# TODO: install node 20 using either n or nvm
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

### Setting up scriptlauncher

Tomatic works alongside an scriptlauncher.
Tomatic redirects to /scriptlauncher,
but scriptlauncher must serve in / so it needs its own domain
and the frontend server must redirect /scriptlauncher
to / on scriptlauncher domain.

Run scriptlauncher passing the `scriptlauncher.yaml` file that comes with Tomatic.

### Setting up minizinc (used by timetable scheduler)

```bash
TARGET_PATH=.venv/bin # or anything in your PATH
wget -q https://github.com/MiniZinc/MiniZincIDE/releases/download/2.7.4/MiniZincIDE-2.7.4-x86_64.AppImage
mv MiniZincIDE-2.7.4-x86_64.AppImage $TARGET_PATH/minizinc
chmod +x $TARGET_PATH/minizinc
minizinc --version
minizinc --help # Should show COIN-BC and Chuffed as "available solvers"
```

### Configuration

- Copy `config-example.yaml` as `config.yaml` and edit it
- Copy `dbconfig-example.py` as `dbconfig.py` and edit it

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

### Configuring the change of shift message

Every shift change tomatic sends a chat.
To customize that message you can create a plain text file as
`data/turn-change-message.txt`

### Setting up Google OAuth2 login

- Go to https://console.cloud.google.com/apis/credentials
- Create a new OAuth2 client id credential
- In dbconfig:
    - Set `tomatic.jwt.secret_key` to whatever you want
    - Set `tomatic.oauth.client_id` to the client id of the created credential
    - Set `tomatic.oauth.client_secret` to the client secret of the created credential

### Setting Up Google Chat Hook

- Go to the Google Chat channel/space you want to notify in
- Go to the channel configuration and then "Applications and integrations"
- Create a new Webhook, setting up the name and the avatar
- Copy the resulting URL
- Set up `tomatic.monitorChatChannel` at `dbconfig.py` with such URL

### Setting Dummy Call Registry

Using a dummy backend for the call registry requires
a categories file. You can take it from an existing
properly setup odoo with:

```bash
tomatic_retrieve.py callcategories
```

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

## How to get an updated node environment

```bash
sudo npm install -g n # Install n (node version chooser)
sudo n stable  # Install stable as option
sudo n # choose the current version
```

And then you need to start a new shell session to see the changes
