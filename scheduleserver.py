# -*- coding: utf-8 -*-
from flask import Flask
from htmlgen import HtmlGenFromYaml
from datetime import datetime
from yamlns import namespace as ns

app = Flask(__name__)


def loadYaml(yaml):
    global h
    h=HtmlGenFromYaml(ns.loads(yaml))

@app.route('/getqueue/<setmana>/<hour>/<minute>')
def get_queue(setmana,hour,minute):
    year,month,day=(int(tok) for tok in setmana.split('_'))
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
