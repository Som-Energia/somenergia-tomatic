"""
Rename this file as dbconfig.py and modify it.
"""

from yamlns import namespace as ns

tomatic=ns(
    # local timetable storage directory
    storagepath='/home/vokimon/somenergia/somenergia-tomatic/graelles',

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

    # from and to mails for daily stats report
    dailystats = ns(
        sender = 'tomatic@mycompany.com',
        recipients = [
            'supervisor@mycompany.com',
        ],
    ),
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

