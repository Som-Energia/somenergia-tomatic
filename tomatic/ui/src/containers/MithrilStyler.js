// MithrilStyler
//
// Mithril function that generates a wrapped component.
// The wrapping provides style and parent context that the
// original mithril Tomatic components had, so that they
// look and behave similar.

import m from 'mithril'
import { Dialog } from 'polythene-mithril-dialog'
import * as css from 'polythene-css'
import PersonStyles from '../mithril/components/personstyles'
import '../mithril/style.styl'
import Tomatic from '../services/tomatic'

Tomatic.onKumatoChanged.push(() => m.redraw())

css.addLayoutStyles()
css.addTypography()
const MithrilStyler = (mithrilComponent) => {
  return {
    view: (vnode) => {
      return m(
        '#tomatic.main.variant-' + Tomatic.variant,
        m(
          '',
          PersonStyles(),
          m(Tomatic.isKumatoMode() ? '.pe-dark-tone' : '', [
            m(mithrilComponent),
            m(Dialog),
          ]),
        ),
      )
    },
  }
}

export default MithrilStyler
