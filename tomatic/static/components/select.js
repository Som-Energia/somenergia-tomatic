'use strict';
module.exports = function() {

    var m = require('mithril');

	m.prop = require('mithril/stream');
	m.component=m;


    var Select = {
        controller: function(attrs) {
            return {
                value: m.prop(attrs.value),
            };
        },
        view: function(ctrl, attrs) {
            console.debug("Select view: ", attrs.value, ctrl.value());
            return m('.pe-textfield.pe-textfield--floating-label'+
                    '.pe-textfield--hide-clear.pe-textfield--dirty', [
                m('.pe-textfield__input-area', [
                    m('label.pe-textfield__label', attrs.label),
                    m('select.pe-textfield__input', {
                        value: ctrl.value(),
                        onchange: function(ev) {
                            ctrl.value(ev.target.value);
                            attrs.onChange(ev);
                        },
                    },
                    Object.keys(attrs.options).map(function(value) {
                        return m('option', {
                            value: value,
                        }, attrs.options[value]);
                    })),
                ]),
            ]);
        },
    };

	return Select;
}();

// vim: noet ts=4 sw=4
