# -*- coding: utf-8 -*-
from flask import Flask
from htmlgen import HtmlGenFromYaml, HtmlGenFromAsterisk
from datetime import datetime
from yamlns import namespace as ns

hs = {}

def pbx(alternative = None):
    if alternative:
        pbx.cache = alternative
    if not hasattr(pbx,'cache'):
        pbx.cache = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
    return pbx.cache

config=None
try:
    import config
except ImportError:
    pass
if config or True:
    import asterisk
    from paramiko import SSHClient,AutoAddPolicy
    from Asterisk.Manager import Manager
app = Flask(__name__)
startOfWeek = HtmlGenFromYaml.iniciSetmana(
    datetime.now()
)
def loadYaml(yaml):
    global hs
    parsedYaml = ns.loads(yaml)
    week = str(parsedYaml.setmana)
    setmana_underscore = week.replace("-","_")
    hs[setmana_underscore]=HtmlGenFromYaml(parsedYaml)

def loadAsterisk(yaml,date=None):
    global hs
    hs[startOfWeek.strftime("%Y_%m_%d")
        ]=HtmlGenFromAsterisk(
            yaml,pbx().receiveConf()
        )
def setNow(year,month,day,hour,minute):
    global now
    now=datetime(year,month,day,hour,minute)

@app.route('/')
def index():
    global now
    if not now:
        now=datetime.now()
    return get_queue(
        "_".join([
            str(now.year),
            "%02d" % now.month,
            "%02d" % now.day]),
        now.hour,
        now.minute
    )

@app.route('/getqueue/<setmana>/<hour>/<minute>')
def get_queue(setmana,hour,minute):
    loadAsterisk(yaml)
    year,month,day=(
        int(tok)
        for tok
        in setmana.split('_')
    )
    startOfWeek = HtmlGenFromYaml.iniciSetmana(
        datetime(year,month,day)
    )
    h = hs[startOfWeek.strftime("%Y_%m_%d")]
    day,turn = h.getCurrentQueue(
        datetime(year,month,day,int(hour),int(minute))
    )
    response = (h.htmlHeader()+
        h.htmlColors()+
        h.htmlSubHeader()+
        h.htmlSetmana()+
        h.partialCurrentQueue(day,turn)+
        h.htmlExtensions()+
        h.htmlFixExtensions()+
        h.htmlFooter()
    )
    return response


now = None
yaml = ns.load("templateTimetable.yaml")
yaml.setmana = startOfWeek.strftime("%Y-%m-%d")

