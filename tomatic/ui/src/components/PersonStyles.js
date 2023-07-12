import React from 'react'
import Tomatic from '../services/tomatic'
import luminance from'./colorutils'
import contrast from './colorutils'


function PersonStyles() {
	var persons = Tomatic.persons()
    return (
		<style dangerouslySetInnerHTML= {{ __html:
			Object.keys(persons.colors || {}).map((name) => {
				var color = '#' + persons.colors[name]
				var darker = '#' + luminance.luminance(color, -0.3)
				var linecolor = contrast.contrast(persons.colors[name])
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
			}).join('\n')
		}} />
    )
}

export default PersonStyles