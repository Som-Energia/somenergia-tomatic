# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()

from flask import (
    Flask,
    Blueprint,
    redirect,
    send_file,
    )
from execution import Execution


api = Blueprint("Background runner", __name__)

@api.route('/')
def default():
    return redirect('/list')

@api.route('/list')
def list():
    return  "\n".join([
        """<p><a href='/run'>New</a></p>"""
    ]+[
        """\
        <li>
            <a href='/status/{name}'>{name}</a>
            {state}
            <a style='display:{killDisplay}' href='/stop/{name}'>Stop</a>
        </li>
        """.format(**execution.listInfo())
        for execution in Execution.list()
    ])

@api.route('/run')
def run():
    execution = Execution.start()
    return redirect("/list".format(execution))

@api.route('/status/<execution>')
def status(execution):
    executionOutput = Execution(execution).outputFile
    return send_file(str(executionOutput))

@api.route('/stop/<execution>')
def stop(execution):
    execution = Execution(execution)
    execution.stop()
    return redirect("/list", code=302)

if __name__ == '__main__':
    app = Flask("Background runner")
    app.register_blueprint(api)
    app.run()


# vim: ts=4 sw=4 et
