var css = require('@emotion/css').css
var m = require('mithril')
var Tomatic = require('../../services/tomatic')

const styles = {
  weeks: css`
    label: weeks;
    display: inline-block;
    width: 100%;
  `,
  week: css`
    label: week;
    cursor: pointer;
    text-align: center;
    padding: 3px;
    color: black;
    background: #ccc;
    :hover {
      background: #bcb;
    }
  `,
  current: css`
    label: current;
    font-weight: bold;
    background: #7a7;
    :hover {
      /* week:hover would be stronger */
      background: #7a7;
    }
    :before {
      content: '►';
    }
    :after {
      content: '◄';
    }
  `,
}

var WeekPicker = {
  oninit: function (vnode) {
    vnode.state.model = this
    vnode.state.setCurrent = function (week) {
      Tomatic.requestGrid(week)
    }
  },
  view: function (c) {
    return m(
      '.weeks',
      { className: styles.weeks },
      Tomatic.weeks().map(function (week) {
        var current = Tomatic.currentWeek() === week ? '.current' : ''
        return m(
          '.week' + current,
          {
            className: styles.week + ' ' + (current && styles.current),
            onclick: function () {
              c.state.setCurrent(week)
            },
          },
          'Setmana del ' + week,
        )
      }),
    )
  },
}

module.exports = WeekPicker

// vim: et sw=2 ts=2
