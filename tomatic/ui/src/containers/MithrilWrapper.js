import * as React from 'react'
import m from 'mithril'

export default function MithrilWrapper({ component }) {
  const root = React.useRef()
  React.useEffect(() => {
    m.mount(root.current, component)
    return () => {
      m.redraw()
    }
  }, [component])

  return <div ref={root}>Loading...</div>
}
