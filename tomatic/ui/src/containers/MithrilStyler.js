// MithrilStyler
//
// Provides style and wrapping the mithril components had
// in the original mithril application so that they look
// and behave properly.

import * as React from 'react'
import m from 'mithril'
import { Dialog } from 'polythene-mithril-dialog'
import * as css from 'polythene-css'
import PersonStyles from '../mithril/components/personstyles'
import customStyle from '../mithril/style.styl'
import Tomatic from '../services/tomatic'

css.addLayoutStyles()
css.addTypography()
console.log('customStyle', customStyle)
const MithrilStyler = (mithrilComponent) => {
  return {
    view: (vnode) => {
      return m(
        '#tomatic.main.variant-' + Tomatic.variant,
        m(
          '',
          PersonStyles(),
          m(Tomatic.isKumatoMode() ? 'pe-dark-tone' : '', [
            m(mithrilComponent),
            m(Dialog),
          ])
        )
      )
    },
  }
}

export default MithrilStyler
