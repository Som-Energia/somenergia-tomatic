// Tomatic application model component
import m from 'mithril'
import prop from 'mithril/stream'
import api from './api'
import subscriptable from './subscriptable'
m.prop = prop

const Tomatic = {
  packageinfo: {
    name: process.env.REACT_APP_NAME,
    version: process.env.REACT_APP_VERSION,
  },
}

Tomatic.variant = 'tomatic'

Tomatic.loggers = []
Tomatic.addLogger = function (logger) {
  this.loggers.push(logger)
}
Tomatic.queue = m.prop([])
Tomatic.persons = subscriptable(m.prop({}))
Tomatic.init = function () {
  this.checkVersionPeriodically()
  this.requestWeeks()
  this.updateQueuePeriodically()
  this.requestPersons()
  this.initKumato()
  this.requestForcedTurns()
}

Tomatic.versionTimer = 0
Tomatic.checkVersionPeriodically = function () {
  console.log('Checking version')
  clearTimeout(Tomatic.versionTimer)
  Tomatic.versionTimer = setTimeout(
    Tomatic.checkVersionPeriodically,
    30 * 60 * 1000,
  )
  Tomatic.checkVersion()
}

Tomatic.checkVersion = function () {
  api
    .request({
      url: '/api/version',
    })
    .then(function (response) {
      Tomatic.variant = response.variant
      if (response.version === Tomatic.packageinfo.version) return
      console.log(
        'New server version',
        response.version,
        'detected.',
        'Frontend version is ',
        Tomatic.packageinfo.version,
        '.',
        'Reloading in 10s...',
      )
      Tomatic.error(
        'Detectada nova versió en el servidor. Recarregant pàgina en 10 segons.',
      )
      setTimeout(function () {
        window.location.reload(true) // True to force full reload
      }, 10000)
    })
}

Tomatic.initKumato = function () {
  // Dark interface
  Tomatic._kumato = JSON.parse(localStorage.getItem('kumato', false))
  Tomatic.isKumatoMode.notify()
}
Tomatic.toggleKumato = function () {
  Tomatic._kumato = !Tomatic._kumato
  localStorage.kumato = Tomatic._kumato
  Tomatic.isKumatoMode.notify()
}
Tomatic.isKumatoMode = subscriptable(function () {
  return Tomatic._kumato
})

// Persons management
Tomatic.requestPersons = function () {
  return api
    .request({
      url: '/api/persons',
    })
    .then(function (response) {
      if (response.persons !== undefined) {
        Tomatic.persons(response.persons)
        Tomatic.persons.notify()
      }
    })
}

// Line management

Tomatic.requestQueue = function (suffix) {
  api
    .request({
      url: '/api/queue' + (suffix || ''),
    })
    .then(function (response) {
      if (response?.currentQueue !== undefined) {
        Tomatic.queue(response.currentQueue)
      }
    })
}

Tomatic.addLine = function (line) {
  Tomatic.requestQueue('/add/' + line)
}

Tomatic.pauseLine = function (line) {
  Tomatic.requestQueue('/pause/' + line)
}

Tomatic.restoreLine = function (line) {
  Tomatic.requestQueue('/resume/' + line)
}

const queueRefreshPeriodSeconds = 2 * 60 // TODO: config param
Tomatic.queueTimer = 0
Tomatic.updateQueuePeriodically = function () {
  console.log('Refreshing queue')
  clearTimeout(Tomatic.queueTimer)
  Tomatic.queueTimer = setTimeout(
    Tomatic.updateQueuePeriodically,
    queueRefreshPeriodSeconds * 1000,
  )
  Tomatic.requestQueue()
}

Tomatic.weekdays = {
  dl: 'Dilluns',
  dm: 'Dimarts',
  dx: 'Dimecres',
  dj: 'Dijous',
  dv: 'Divendres',
}

/* Forced Turns */
Tomatic.forcedTurns = subscriptable(m.prop({}))
Tomatic.requestForcedTurns = function () {
  api
    .request({
      url: '/api/forcedturns',
    })
    .then(function (data) {
      if (!data) return
      data.days = data.days || 'dl dm dx dj dv'.split(' ')
      delete data.colors
      delete data.names
      delete data.extensions
      delete data.tables // TODO: This one was never added
      Tomatic.forcedTurns(data)
      Tomatic.forcedTurns.notify()
    })
}
Tomatic.forcedTurnCell = function (day, houri, turni) {
  try {
    return Tomatic.forcedTurns().timetable[day][houri][turni]
  } catch (err) {
    return undefined
  }
}

Tomatic.editForcedTurn = function (day, houri, turni, name) {
  // Direct edition, just for debug purposes
  //Tomatic.grid().timetable[day][houri][turni] = name;
  api
    .request({
      method: 'PATCH',
      url: '/api/forcedturns/' + [day, houri, turni, name].join('/'),
    })
    .then(
      function (data) {
        Tomatic.requestForcedTurns()
      },
      function (error) {
        Tomatic.error(
          'Problemes editant els torns fixos: ' + (error || 'Inexperat'),
        )
      },
    )
}

Tomatic.forcedTurnsAddColumn = function () {
  api
    .request({
      method: 'PATCH',
      url: '/api/forcedturns/addColumn',
    })
    .then(
      function (data) {
        Tomatic.requestForcedTurns()
      },
      function (error) {
        Tomatic.error('Problemes editant la graella: ' + (error || 'Inexperat'))
      },
    )
}

Tomatic.forcedTurnsRemoveColumn = function () {
  api
    .request({
      method: 'PATCH',
      url: '/api/forcedturns/removeColumn',
    })
    .then(
      function (data) {
        Tomatic.requestForcedTurns()
      },
      function (error) {
        Tomatic.error('Problemes editant la graella: ' + (error || 'Inexperat'))
      },
    )
}

Tomatic.grid = subscriptable(m.prop({}))
Tomatic.requestGrid = function (week) {
  api
    .request({
      url: '/api/graella-' + week + '.yaml',
    })
    .then(function (data) {
      data.days = data.days || 'dl dm dx dj dv'.split(' ')
      delete data.colors
      delete data.names
      delete data.extensions
      delete data.tables // TODO: This one was never added
      Tomatic.currentWeek(week)
      Tomatic.grid(data)
      Tomatic.grid.notify()
    })
}
Tomatic.weekday = function (short, alternative) {
  return Tomatic.weekdays[short] || alternative || '??'
}
Tomatic.personColor = function (name) {
  if (!Tomatic.persons().colors) {
    return '#aaaaaa'
  }
  return Tomatic.persons().colors[name]
}
Tomatic.nameInitials = function (name) {
  return Tomatic.formatName(name)
    .split('')
    .filter((l) => l.trim().toUpperCase() === l)
    .slice(0, 2)
    .join('')
}
Tomatic.formatName = function (name) {
  function titleCase(str) {
    return str.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
  }
  if (!name) {
    return '-'
  }
  return (Tomatic.persons().names || {})[name] || titleCase(name)
}
Tomatic.formatExtension = function (name) {
  return (Tomatic.persons().extensions || {})[name] || '???'
}
Tomatic.table = function (name) {
  var tables = Tomatic.persons().tables
  if (!tables) {
    Tomatic.persons().tables = {}
  } // TODO: Move that anywhere else
  var table = Tomatic.persons().tables[name]
  if (table === undefined) {
    return -1
  }
  return table
}
Tomatic.peopleInTable = function (table) {
  var tables = Tomatic.persons().tables || {}
  var result = Object.keys(tables).filter(function (k) {
    return Tomatic.table(k) === table
  })
  return result
}
Tomatic.cell = function (day, houri, turni) {
  try {
    return Tomatic.grid().timetable[day][houri][turni]
  } catch (err) {
    return undefined
  }
}
Tomatic.editCell = function (day, houri, turni, name, myname) {
  // Direct edition, just for debug purposes
  //Tomatic.grid().timetable[day][houri][turni] = name;
  api
    .request({
      method: 'PATCH',
      url:
        '/api/graella/' +
        [Tomatic.grid().week, day, houri, turni, name].join('/'),
      body: myname,
    })
    .then(
      function (data) {
        Tomatic.requestGrid(Tomatic.grid().week)
      },
      function (error) {
        Tomatic.error('Problemes editant la graella: ' + (error || 'Inexperat'))
      },
    )
}

Tomatic.deletePerson = function (id) {
  api
    .request({
      method: 'DELETE',
      url: '/api/person/' + id,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        console.log(error)
        Tomatic.error(
          'Problemes esborrant la persona: ' + (error.error || 'Inexperat'),
        )
      },
    )
}

Tomatic.setPersonDataReact = function (id, data) {
  if (id === undefined) {
    id = data.id
  }
  var postdata = {}

  for (var key in data) {
    var value = data[key]
    switch (key) {
      case 'name':
        delete Tomatic.persons().names[id]
        var formatName = Tomatic.formatName(id)
        if (formatName !== value) {
          postdata.name = value
        }
        break
      case 'extension':
        postdata.extension = value
        break
      case 'table':
        postdata.table = parseInt(value, 10)
        break
      case 'color':
        postdata.color = value
        break
      case 'email':
        postdata.email = value
        break
      case 'erpuser':
        postdata.erpuser = value
        break
      case 'idealload':
        const newLoad = parseInt(value)
        postdata.idealload = isNaN(newLoad) ? null : newLoad
        break
      case 'groups':
        postdata.groups = value
        break
      case 'id':
        // ignore
        break
      default:
        console.log('Unexpected person parameter', key)
        break
    }
  }
  console.log('posting', postdata)
  api
    .request({
      method: 'POST',
      url: '/api/person/' + id,
      body: postdata,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        console.log(error)
        Tomatic.error(
          'Problemes editant la persona: ' + (error.error || 'Inexperat'),
        )
      },
    )
}
Tomatic.setPersonData = function (name, data) {
  if (name === undefined) {
    name = data.name
  }
  var postdata = {}

  for (var key in data) {
    var value = data[key]
    switch (key) {
      case 'formatName':
        postdata.name = value
        break
      case 'extension':
        postdata.extension = value
        break
      case 'table':
        postdata.table = parseInt(value, 10)
        break
      case 'color':
        postdata.color = value
        break
      case 'email':
        postdata.email = value
        break
      case 'erpuser':
        postdata.erpuser = value
        break
      case 'idealload':
        postdata.idealload = value
        break
      default:
        console.log('Unexpected person parameter', key)
        break
    }
  }
  console.log('posting', postdata)
  api
    .request({
      method: 'POST',
      url: '/api/person/' + name,
      body: postdata,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        console.log(error)
        Tomatic.error(
          'Problemes editant la persona: ' + (error.error || 'Inexperat'),
        )
      },
    )
}

Tomatic.weeks = subscriptable(m.prop([]))
Tomatic.currentWeek = m.prop(undefined)
Tomatic.requestWeeks = function () {
  api
    .request({
      url: '/api/graella/list',
    })
    .then(function (newWeeklist) {
      if (!newWeeklist) return
      var weeks = newWeeklist.weeks.sort().reverse()
      Tomatic.weeks(weeks)
      if (Tomatic.currentWeek() === undefined) {
        var expirationms = 1000 * 60 * 60 * (24 * 4 + 18)
        var oldestWeek = new Date(new Date().getTime() - expirationms)
        var current = undefined
        for (var i in weeks) {
          if (current !== undefined && new Date(weeks[i]) < oldestWeek) {
            break
          }
          current = weeks[i]
        }
        if (current !== undefined) {
          Tomatic.requestGrid(current)
        }
      }
      Tomatic.weeks.notify()
    })
}

Tomatic.log = function (message) {
  console.log('log: ', message)
  Tomatic.loggers.forEach((logger) => {
    logger.log(message)
  })
}

Tomatic.error = function (message) {
  console.log('error: ', message)
  Tomatic.loggers.forEach((logger) => {
    logger.error(message)
  })
}

Tomatic.sendBusyData = function (name, data) {
  console.log('updating', name, '/api/busy/' + name)
  api
    .request({
      method: 'POST',
      url: '/api/busy/' + name,
      body: data,
    })
    .then(
      function (response) {
        console.debug('Busy POST Response: ', response)
        if (response.result === 'ok') {
          return
        }
        console.debug('apicall failed:', response.error)
        Tomatic.error(
          'Problemes desant les indisponibilitats: ' + response.message,
        )
      },
      function (error) {
        console.debug('Busy POST apicall failed:', error)
        Tomatic.error(
          'Problemes desant les indisponibilitats: ' + (error || 'Inexperat'),
        )
      },
    )
}

Tomatic.retrieveBusyData = function (name, callback) {
  console.log('retrieving', name, '/api/busy/' + name)
  api
    .request({
      url: '/api/busy/' + name,
    })
    .then(
      function (response) {
        console.debug('Busy GET Response: ', response)
        callback(response)
        if (response.errors && response.errors.lenght) {
          Tomatic.error(
            'Problemes carregant a les indisponibilitats:\n' +
              response.errors.join('\n'),
          )
        }
      },
      function (error) {
        console.debug('Busy GET apicall failed:', error)
        Tomatic.error(
          'Problemes carregant a les indisponibilitats: ' +
            (error || 'Inexperat'),
        )
      },
    )
}
Tomatic.retrieveBusyDataFake = function (name, callback) {
  console.log('simulating retrieval', name)
  setTimeout(function () {
    callback({
      oneshot: [
        {
          date: '2013-06-23',
          turns: '0011',
          optional: true,
          reason: 'motivo 0',
        },
        {
          date: '2013-12-23',
          turns: '0110',
          optional: false,
          reason: 'motivo 1',
        },
        {
          date: '2017-02-23',
          turns: '1100',
          optional: true,
          reason: 'motivo 2',
        },
        {
          date: '2019-12-25',
          turns: '1111',
          optional: false,
          reason: 'me quedo en casa rascandome los gatos',
        },
      ],
      weekly: [
        {
          weekday: 'dm',
          turns: '1111',
          optional: false,
          reason: 'motivo 3',
        },
        {
          weekday: '',
          turns: '0011',
          optional: false,
          reason: 'me quedo en casa rascandome los gatos',
        },
      ],
    })
  }, 1000)
}

export default Tomatic

// vim: et ts=2 sw=2
