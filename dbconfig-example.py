"""
Rename this file as dbconfig.py and modify it.
"""

from yamlns import namespace as ns

tomatic=ns(
    # local timetable storage directory
    storagepath='/home/vokimon/somenergia/somenergia-tomatic/graelles',
    # Choose the PBX backend:
    # - fake: emulates a real PBX
    # - asteriskcli: connects asterisk by ssh
    # - asteriskdb: connects asterist by mysql connection
    # - irontec: connects to the Irontec API
    # - areavoip: connnects to the AreaVoip API
    # You can add your own backend as submodule to tomatix.pbx
    pbx='irontec',
    # Define this if realtime database is used to control asterisk
    # this holds ponyorm parameters, positional as args and keyword as kwds
    no_dbasterisk=ns(
        args=['mysql'],
        kwds=ns(
            host='localhost',
            port=3000,
            user='asterisk',
            passwd='asterisk',
            db='asterisk',
        ),
    ),
    # Define this if remote cli is used to access asterisk
    no_ssh = ns(
        username='user',
        password='mypassword',
        host='192.168.23.1',
    ),
    # Define this if areavoip api is used to access asterisk
    no_areavoip = ns(
        baseurl = 'https://vpbx2.nubelfon.com/pbx/proxyapi.php',
        apikey = 'xxxxxxxxxxxx',
        tenant = 'MyCompany',
        queue = 666,
    ),
    # configure this to have an html timetable published by scp
    no_publishStatic = ns(
        host='web.mycompany.com',
        user='webmaster',
        path='/home/webmaster/timetables/',
    ),
    # Configure this to download vacations from Notoi API
    no_notoi_data = ns(
        service_url = "https://....",
        user = "myuser",
        password = "mypassword",
    ),
    # Configure this to download vacations from odoo
    no_holidaysodoo = ns(
        server='https://xxx.xxx.xxx.xxx:xxxx',
        db="odoo",
        user="tomatic",
        password="mypasword",
    ),

    # from and to mails for daily stats report
    dailystats = ns(
        sender = 'tomatic@mycompany.com',
        recipients = [
            'supervisor@mycompany.com',
        ],
    ),
    # Hangout channel to warn managers
    monitorChatChannel = 'Telefon',
)
# Used to send mails
smtp = ns(
   host = 'smtp.mycompany.com',
   port = 587,
   user = 'tomatic@mycompany.com',
   password = 'mypassword',
)

# This should be configured to access your openerp/odoo instance
# Tomatic uses this to provide the CRM view
erppeek = ns(
    server='https://xxx.xxx.xxx.xxx:xxxx',
    db="myerp",
    user="tomatic",
    password="mypasword",
)

