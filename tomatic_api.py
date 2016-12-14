# -*- coding: utf-8 -*-

from  tomatic.api import app

if __name__ == '__main__':
    print app
    for rule in app.url_map.iter_rules():
        print rule
    app.run(debug=True, host='0.0.0.0', processes=1)

