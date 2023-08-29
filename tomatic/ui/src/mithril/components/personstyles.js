var m = require('mithril')
var Tomatic = require('../../services/tomatic')
var luminance = require('../components/colorutils').luminance
var contrast = require('../components/colorutils').contrast

const PersonStyles = function () {
  var persons = Tomatic.persons()
  return m(
    'style',
    Object.keys(persons.colors || {}).map(function (name) {
      var color = '#' + persons.colors[name]
      var darker = '#' + luminance(color, -0.3)
      var linecolor = contrast(persons.colors[name])
      return (
        `.${name}, .graella .${name} {\n` +
        `  background-color: ${color};\n` +
        `  border-color: ${darker};\n` +
        `  border-width: 20pt;\n` +
        `  color: ${linecolor};\n` +
        `}\n` +
        `.pe-dark-theme .${name}, .pe-dark-theme .graella .${name} {\n` +
        `  background-color: ${darker};\n` +
        `  border-color: ${color};\n` +
        `  border-width: 2pt;\n` +
        `  color: ${linecolor};\n` +
        `}\n`
      )
    }),
  )
}

export default PersonStyles

// vim: noet ts=4 sw=4
