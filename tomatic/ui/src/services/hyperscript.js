import React from 'react'
/**
Emulates mithril hyperscript funtionality in React.
Useful to quickly port mithril code but not fully reliable.

Limitations:

- It does not support mithril components as part of the hyperscript.
- Only supports selectors with tags and classes.
  For instance, ids and attribute selectors will mess the output.
- It won't generate keys on arrays which are required for React.
*/

export default function m(...args) {
  function isobject(x) {
    return typeof x === 'object' && !x['$$typeof']
  }
  const type = args[0].split('.')[0] || 'div'
  const attributes = Object.assign({}, ...args.slice(1).filter(isobject))
  const classes = (attributes.className ?? '').split(' ')
  classes.concat(args[0].split('.').slice(1))
  attributes.className = classes.join(' ')
  const children = args.slice(1).filter((x) => !isobject(x))
  return React.createElement(type, attributes, ...children)
}
