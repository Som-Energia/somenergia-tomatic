// Tomatic application model component
import m from 'mithril'
import prop from 'mithril/stream'
import api from './api'
import messages from './messages'
import { preferedWeek } from './dateutils'
import subscriptable from './subscriptable'
import {prop as reactiveProp} from './subscriptable'
m.prop = prop

const Tomatic = {
  packageinfo: {
    name: process.env.REACT_APP_NAME,
    version: process.env.REACT_APP_VERSION,
  },
}

Tomatic.init = function () {
  console.log("Initialization Tomatic")
  this.checkVersionPeriodically()
  this.initKumato()
  this.updateQueuePeriodically()
  this.requestWeeks()
  this.requestPersons()
  this.requestForcedTurns()
}

// Server version

Tomatic.variant = 'tomatic'
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
  const context = `Obtenint la versió del servidor`
  api
    .request({
      context,
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
      messages.error(
        'Detectada nova versió en el servidor. Recarregant pàgina en 10 segons.',
      )
      setTimeout(function () {
        window.location.reload(true) // True to force full reload
      }, 10000)
    })
}

// Kumato mode (Dark Interface)

Tomatic.initKumato = function () {
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

Tomatic.persons = reactiveProp({})
Tomatic.requestPersons = function () {
  return api
    .request({
      url: '/api/persons',
    })
    .then(function (response) {
      if (response.persons !== undefined) {
        Tomatic.persons(response.persons)
      }
    })
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
Tomatic.tableOptions = function () {
  function range(end) {
    if (end < 1) return []
    return [...Array(end).keys()]
  }
  const tables = Tomatic.persons().tables || {}
  const tableMembers = Object.keys(tables).reduce((d, name) => {
    const personTable = tables[name]
    if (personTable === -1) return d
    if (d[personTable] === undefined) {
      d[personTable] = []
    }
    d[personTable].push(name)
    return d
  }, {})

  const result = [[-1, 'Sense taula']]
  const nTables = Math.max(...Object.keys(tableMembers))
  for (const i in range(nTables + 1)) {
    if (tableMembers[i] === undefined) {
      result.push([i, `Taula ${i} amb ningú`])
    } else {
      const people = tableMembers[i].map(Tomatic.formatName).join(', ')
      result.push([i, `Taula ${i} amb ` + people])
    }
  }
  return result
}

Tomatic.allGroups = function () {
  const groups = Tomatic.persons().groups || {}
  return Object.keys(groups)
}
Tomatic.groups = function (name) {
  const groups = Tomatic.persons().groups || {}
  return Object.keys(groups).filter((g) => groups[g].includes(name))
}

Tomatic.personFields = function (name) {
  const persons = Tomatic.persons()
  return {
    id: name,
    name: Tomatic.formatName(name),
    color: persons.colors[name],
    extension: persons.extensions[name],
    email: persons.emails[name],
    erpuser: persons.erpusers[name],
    idealload: persons.idealloads[name],
    table: Tomatic.table(name),
    groups: Tomatic.groups(name),
  }
}

Tomatic.allPeople = function() {
  const persons = Tomatic.persons()
  return Array.from(new Set([
      ...Object.keys(persons.names||{}),
      ...Object.keys(persons.colors||{}),
      ...Object.keys(persons.extensions||{}),
      ...Object.keys(persons.emails||{}),
      ...Object.keys(persons.erpusers||{}),
      ...Object.keys(persons.idealloads||{}),
      ...Object.keys(persons.tables||{}),
  ]))
}

Tomatic.allPeopleData = function() {
  const allNames = Tomatic.allPeople()
  return allNames.map((name)=>Tomatic.personFields(name))
}

Tomatic.deletePerson = function (id) {
  const context = `Esborrant la usuaria '${id}'`
  api
    .request({
      context,
      method: 'DELETE',
      url: '/api/person/' + id,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

Tomatic.setPersonDataReact = function (id, data) {
  const context = `Actualitzant dades de la usuaria ${id}`
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
        messages.warn(`Unexpected person parameter '${key}'`, { context })
        break
    }
  }
  console.log('posting', postdata)
  api
    .request({
      context,
      method: 'POST',
      url: '/api/person/' + id,
      body: postdata,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}
Tomatic.setPersonData = function (name, data) {
  const context = `Actualitzant dades de la usuaria ${name}`
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
      case 'name':
      case 'tables':
      case 'newone':
        console.log({ data, key })
        break
      default:
        messages.warn(`Unexpected person parameter '${key}'`, { context })
        break
    }
  }
  api
    .request({
      context,
      method: 'POST',
      url: '/api/person/' + name,
      body: postdata,
    })
    .then(
      function (data) {
        Tomatic.requestPersons()
      },
      function (error) {
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

//////////////////////
// Line management

Tomatic.queue = reactiveProp([])
//Tomatic.queue.subscribe(()=>console.debug("Updated queue: ", Tomatic.queue()))
Tomatic.requestQueue = function (suffix) {
  api
    .request({
      url: '/api/queue' + (suffix || ''),
    })
    .then(function (response) {
      Tomatic.queue(response?.currentQueue || [])
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

const queueRefreshPeriodSeconds = 5 //2 * 60 // TODO: config param
// Use window to have a true shared value.
// Avoids duppes on hot module reload.
window.tomaticQueueTimer = 0

Tomatic.updateQueuePeriodically = function () {
  clearTimeout(window.tomaticQueueTimer)
  window.tomaticQueueTimer = setTimeout(
    Tomatic.updateQueuePeriodically,
    queueRefreshPeriodSeconds * 1000,
  )
  Tomatic.requestQueue()
}

///////////////////////
// Forced turns

Tomatic.forcedTurns = reactiveProp({})
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
  const context = `Editant el torn forçat ${day} ${houri} ${turni} ${name}`
  api
    .request({
      context,
      method: 'PATCH',
      url: '/api/forcedturns/' + [day, houri, turni, name].join('/'),
    })
    .then(
      function (data) {
        Tomatic.requestForcedTurns()
      },
      function (error) {
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

Tomatic.forcedTurnsAddColumn = function () {
  const context = `Afegint línia als torns fixos`
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
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

Tomatic.forcedTurnsRemoveColumn = function () {
  const context = `Eliminant linia als torns fixos`
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
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

////////////////
// Timetable

Tomatic.grid = reactiveProp({})
Tomatic.requestGrid = function (week) {
  if (week === undefined) {
    Tomatic.grid({})
    return
  }
  api
    .request({
      url: '/api/graella-' + week + '.yaml',
    })
    .then(function (data) {
      data.days = data.days || 'dl dm dx dj dv'.split(' ')
      // TODO: Delete on API
      delete data.colors
      delete data.names
      delete data.extensions
      delete data.tables // TODO: This one was never added
      Tomatic.grid(data)
    })
}

Tomatic.weekdays = {
  dl: 'Dilluns',
  dm: 'Dimarts',
  dx: 'Dimecres',
  dj: 'Dijous',
  dv: 'Divendres',
}

Tomatic.weekday = function (short, alternative) {
  return Tomatic.weekdays[short] || alternative || '??'
}

// TODO: Make it independent of grid
Tomatic.hourLabel = function(i) {
  const { hours } = Tomatic.grid()
  return `${hours[i]} - ${hours[i + 1]}`
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
  const context = `Editant la graella`
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
        Tomatic.requestGrid(Tomatic.currentWeek())
      },
      function (error) {
        messages.error(error || 'Error inexperat', { context })
      },
    )
}

Tomatic.weeks = reactiveProp([])
Tomatic.currentWeek = reactiveProp(undefined)
Tomatic.currentWeek.subscribe(() => {
  Tomatic.requestGrid(Tomatic.currentWeek())
})
Tomatic.requestWeeks = function () {
  api
    .request({
      url: '/api/graella/list',
    })
    .then(function (newWeeklist) {
      if (!newWeeklist) return
      var weeks = newWeeklist.weeks.sort().reverse()
      Tomatic.weeks(weeks)
      Tomatic.currentWeek(preferedWeek(weeks))
    })
}

///////////////////////
// Busy

Tomatic.sendBusyData = function (name, data) {
  const context = `Actualitzant indisponibilitats per ${name}`
  api
    .request({
      context,
      method: 'POST',
      url: '/api/busy/' + name,
      body: data,
    })
    .then(
      function (response) {
        if (response.result === 'ok') {
          return
        }
        messages.error(response.message, { context })
      },
      function (error) {
        messages.error(error?.message || 'Error Inexperat', { context })
      },
    )
}

Tomatic.retrieveBusyData = function (name, callback) {
  const context = `Obtenint indisponibilitats per ${name}`
  api
    .request({
      context,
      url: '/api/busy/' + name,
    })
    .then(
      function (response) {
        callback(response)
        if (response.errors && response.errors.length) {
          messages.error(response.errors.join('\n'), { context })
        }
      },
      function (error) {
        messages.error(error.message || 'Error Inexperat', { context })
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
