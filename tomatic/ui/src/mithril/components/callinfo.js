// This module controls the state regarding the callinfo page
import api from '../../services/api'
import Auth from '../../services/auth'
import subscriptable from '../../services/subscriptable'
import Tomatic from '../../services/tomatic'
import autofiltertype from '../../services/autofiltertype'

var websock = null
var CallInfo = {}
CallInfo.categories = [] // Call categories
CallInfo.sections = [] // Teams to assign a call
CallInfo.currentPerson = 0 // Selected person from search data
CallInfo.currentContract = 0 // Selected contract selected person
CallInfo.updatingCategories = false // Whether we are still loading crm categoies

CallInfo._autoRefresh = true // whether we are auto searching on incomming calls
CallInfo.autoRefresh = subscriptable((...args) => {
  if (args.length === 0) return CallInfo._autoRefresh
  CallInfo._autoRefresh = !!args[0]
  CallInfo.autoRefresh.notify()
})
CallInfo.autoRefresh.toggle = () => {
  CallInfo.autoRefresh(!CallInfo.autoRefresh())
}

CallInfo._search_query = {
  text: '',
  field: 'auto',
}
CallInfo.search_query = subscriptable((...args)=>{
  if (args.length===0) return CallInfo._search_query
  CallInfo._search_query = {...CallInfo._search_query, ...args[0]}
  CallInfo.search_query.notify()
})

CallInfo.call = {
  phone: '', // phone of the currently selected call registry
  date: '', // isodate of the last unbinded search or the currently selected call registry
  category: '', // annotated category for the call
  notes: '', // annotated comments for the call
}
CallInfo.currentCall = subscriptable(() => {
  return CallInfo.call.date
})

CallInfo.savingAnnotation = false
CallInfo.annotation = {}

CallInfo.resetAnnotation = function () {
  var tag = CallInfo.reasonTag()
  CallInfo.annotation = {
    resolution: 'unsolved',
    tag: tag,
  }
}

CallInfo.noSection = 'ASSIGNAR USUARI'
CallInfo.helpdeskSection = 'CONSULTA'
CallInfo.hasNoSection = function () {
  return CallInfo.annotation.tag === CallInfo.noSection
}
CallInfo.reasonTag = function () {
  var category = CallInfo.call.category.description
  if (!category) return ''
  var matches = category.match(/\[(.*?)\]/)
  if (matches) {
    return matches[1].trim()
  }
  return ''
}

var postAnnotation = function (annotation) {
  api
    .request({
      method: 'POST',
      url: '/api/call/annotate',
      body: annotation,
    })
    .then(
      function (response) {
        console.debug('Info POST Response: ', response)
        if (response.info.message !== 'ok') {
          console.debug(
            'Error al desar motius telefon: ',
            response.info.message,
          )
        } else {
          console.debug('INFO case saved')
          CallInfo.deselectLog()
        }
      },
      function (error) {
        console.debug('Info POST apicall failed: ', error)
      },
    )
}

CallInfo.annotationIsClaim = function () {
  return CallInfo.call.category.isclaim
}

CallInfo.saveCallLog = function () {
  CallInfo.savingAnnotation = true
  var partner = CallInfo.selectedPartner()
  var contract = CallInfo.selectedContract()
  var user = Auth.username()
  var partner_code = partner !== null ? partner.id_soci : ''
  var contract_number = contract !== null ? contract.number : ''
  var isodate = CallInfo.call.date || new Date().toISOString()
  var isClaim = CallInfo.annotationIsClaim()
  var claim = CallInfo.annotation
  postAnnotation({
    user: user,
    date: isodate,
    phone: CallInfo.call.phone,
    partner: partner_code,
    contract: contract_number,
    // TODO: Uses structure instead of fragile string to parse
    reason: CallInfo.call.category.description,
    notes: CallInfo.call.notes,
    claimsection: !isClaim
      ? ''
      : claim.tag
      ? claim.tag
      : CallInfo.helpdeskSection,
    resolution: isClaim ? claim.resolution : '',
  })
}

CallInfo.clearAnnotation = function () {
  CallInfo.call.category = ''
  CallInfo.call.notes = ''
  CallInfo.savingAnnotation = false
}

CallInfo._results = {} // Retrieved search data
CallInfo.results = subscriptable((...args)=>{
  if (args.length===0) return CallInfo._results
  CallInfo._results = args[0]
  CallInfo.results.notify()
})

// Nicely clears search results
CallInfo.resetSearch = function () {
  CallInfo.currentPerson = 0
  CallInfo.currentContract = 0
  CallInfo.results({})
}

CallInfo.changeUser = function (newUser) {
  CallInfo.deselectLog()
  CallInfo.personCalls([])
  CallInfo.autoRefresh(true)
}

CallInfo.callReceived = function (date, phone) {
  if (!CallInfo.autoRefresh()) {
    return
  }
  CallInfo.selectLog(date, phone)
}

CallInfo.selectableSections = function () {
  return CallInfo.sections.map(function (section) {
    return section.name
  })
}

function formatContractNumber(number) {
  // some contract numbers get converted  to int and lose their padding
  var result = number + ''
  while (result.length < 7) result = '0' + result
  return result
}

function fixContractNumbers(info) {
  info.partners.forEach(function (partner) {
    partner.contracts.forEach(function (contract) {
      contract.number = formatContractNumber(contract.number)
    })
  })
}

function fixContractNumbersInDetails(response) {
  // KLUDGE: js-yaml parses 09999 as 9999 instead of '09999'
  response.info.info = Object.keys(response.info.info).reduce((result, key) => {
    result[formatContractNumber(key)] = response.info.info[key]
    return result
  }, {})
  return response
}

function contractNumbers(info) {
  var result = {}
  info.partners.forEach(function (partner) {
    partner.contracts.forEach(function (contract) {
      result[contract.number] = contract
    })
  })
  return Object.keys(result)
}

CallInfo.filteredCategories = function (filter, isclaim) {
  var lowerFilter = filter.toLowerCase()
  return CallInfo.categories.filter(function (category) {
    if (isclaim !== category.isclaim) {
      return false
    }
    if (category.description.toLowerCase().includes(lowerFilter)) {
      return true
    }
    if (category.keywords.toLowerCase().includes(lowerFilter)) {
      return true
    }
    return false
  })
}

function isEmpty(obj) {
  return Object.keys(obj).length === 0
}

CallInfo.searchStatus = function () {
  if (isEmpty(CallInfo.results())) {
    return 'ZERORESULTS'
  }
  if (CallInfo.results()[1] === 'empty') {
    return 'SEARCHING'
  }
  if (CallInfo.results()[1] === 'toomuch') {
    return 'TOOMANYRESULTS'
  }
  if (CallInfo.results()[1] === 'error') {
    return 'ERROR'
  }
  return 'SUCCESS'
}

CallInfo.selectedPartner = function () {
  if (!CallInfo.results()) {
    return null
  }
  if (!CallInfo.results().partners) {
    return null
  }
  if (CallInfo.results().partners.length === 0) {
    return null
  }
  var partner = CallInfo.results().partners[CallInfo.currentPerson]
  if (partner === undefined) {
    return null
  }
  return partner
}

CallInfo.selectedContract = function () {
  var partner = CallInfo.selectedPartner()
  if (partner === null) {
    return null
  }
  if (partner.contracts === undefined) {
    return null
  }
  if (partner.contracts.length === 0) {
    return null
  }
  return partner.contracts[CallInfo.currentContract]
}

CallInfo.selectContract = function (idx) {
  CallInfo.currentContract = idx
}

CallInfo.selectPartner = function (idx) {
  CallInfo.currentPerson = idx
  CallInfo.currentContract = 0
}

var retrieveInfo = function () {
  CallInfo.results({ 1: 'empty' }) // Searching...
  const searchValue = CallInfo.search_query().text.trim()
  let searchField = CallInfo.search_query().field
  if (searchField === 'auto') 
    searchField = autofiltertype(searchValue) || 'all'
  const encodedValue = encodeURIComponent(searchValue)
  function exitWithError(msg) {
    Tomatic.error(msg)
    CallInfo.results({ 1: 'error' })
  }

  api
    .request({
      url: '/api/info/' + searchField + '/' + encodedValue,
    })
    .then(
      function (response) {
        console.debug('Info GET Response: ', response)
        if (response.info.message === 'response_too_long') {
          CallInfo.results({ 1: 'toomuch' })
          return
        }
        if (response.info.message === 'no_info') {
          CallInfo.results({})
          return
        }
        if (response.info.message !== 'ok') {
          return exitWithError(
            'Error al obtenir les dades: ' + response.info.message,
          )
        }
        const results = response.info.info
        fixContractNumbers(results)
        CallInfo.results(results)
        if (CallInfo.call.date === '') {
          // TODO: If selection is none
          CallInfo.call.date = new Date().toISOString()
        }
        // Keep the context, just in case a second query is started
        // and CallInfo.results() is overwritten
        var context = CallInfo.results()
        api
          .request({
            method: 'POST',
            url: '/api/info/contractdetails',
            body: {
              contracts: contractNumbers(context),
            },
          })
          .then(fixContractNumbersInDetails)
          .then(function (response) {
            context.partners.forEach(function (partner) {
              partner.contracts.forEach(function (contract) {
                var number = formatContractNumber(contract.number)
                var retrieved = response.info.info[number]
                if (retrieved === undefined) {
                  return exitWithError(
                    'No extended contract info for contract' + number,
                  )
                }
                contract.invoices = retrieved.invoices
                contract.lectures_comptadors = retrieved.lectures_comptadors
                contract.atr_cases = retrieved.atr_cases
                CallInfo.results.notify()
              })
            })
          })
      },
      function (error) {
        return exitWithError('Info GET apicall failed: ' + error)
      },
    )
}

CallInfo.notifyUsage = function (event) {
  api.request({
    method: 'POST',
    url: '/api/logger/' + event,
    body: {
      user: Auth.username(),
    },
  })
}

CallInfo.getCategories = function () {
  api
    .request({
      url: '/api/call/categories',
    })
    .then(
      function (response) {
        console.debug('Categories GET Response: ', response)

        if (!response) return

        CallInfo.categories = response.categories
        CallInfo.categories.forEach(function (category) {
          var section = category.section
          if (section === null) {
            section = CallInfo.noSection
          }
          if (section === 'HelpDesk') {
            section = CallInfo.helpdeskSection
          }
          category.description =
            '[' + section + '] ' + category.code + '. ' + category.name
        })
        CallInfo.sections = response.sections
      },
      function (error) {
        console.debug('Info GET apicall failed: ', error)
      },
    )
}

CallInfo.updateCategories = function () {
  CallInfo.updatingCategories = true
  api
    .request({
      url: '/api/call/categories/update',
    })
    .then(
      function (response) {
        console.debug('Info GET Response: ', response)
        if (response.info.message !== 'ok') {
          console.debug(
            'Error al actualitzar les categories de trucades telefòniques: ',
            response.info.message,
          )
        } else {
          CallInfo.updatingCategories = false
          CallInfo.getCategories()
        }
      },
      function (error) {
        console.debug('Info GET apicall failed: ', error)
      },
    )
}

CallInfo.callLog = [] // User call registry
CallInfo.personCalls = subscriptable((...args) => {
  if (args.length === 0) return CallInfo.callLog
  CallInfo.callLog = args[0]
  CallInfo.personCalls.notify()
})

CallInfo.retrievePersonCalls = function () {
  var username = Auth.username()
  if (username === -1 || username === '') {
    CallInfo.personCalls([])
    return 0
  }
  CallInfo.personCalls(['lookingfor'])
  api
    .request({
      url: '/api/personlog/' + username,
    })
    .then(
      function (response) {
        console.debug('Info GET Response: ', response)
        if (response.info.message !== 'ok') {
          console.debug(
            'Error al obtenir trucades ateses.',
            response.info.message,
          )
          CallInfo.personCalls([])
        } else {
          CallInfo.personCalls(response.info.info)
        }
      },
      function (error) {
        CallInfo.personCalls([])
        console.debug('Info GET apicall failed: ', error)
      },
    )
}

CallInfo.isLogSelected = function (date) {
  return CallInfo.call.date === date
}

CallInfo.selectLog = function (date, phone) {
  CallInfo.clearAnnotation()
  CallInfo.resetSearch()
  CallInfo.call.date = date
  CallInfo.call.phone = phone
  CallInfo.search_query({
    text: phone,
    field: 'phone',
  })
  CallInfo.currentCall.notify()
  retrieveInfo()
}

CallInfo.deselectLog = function () {
  CallInfo.clearAnnotation()
  CallInfo.resetSearch()
  CallInfo.call.date = ''
  CallInfo.call.phone = ''
  CallInfo.search_query({text: ''})
  CallInfo.currentCall.notify()
}

CallInfo.toggleLog = function (date, phone) {
  //console.log("Toggling", date, phone, CallInfo.call.date);
  if (CallInfo.isLogSelected(date)) {
    CallInfo.deselectLog()
  } else {
    CallInfo.selectLog(date, phone)
  }
}

CallInfo.searchCustomer = function () {
  // clear
  CallInfo.clearAnnotation()
  CallInfo.resetSearch()
  // end of clear
  if (CallInfo.search_query().text === '') return
  retrieveInfo()
}

var connectWebSocket = function () {
  var url = new URL('/backchannel', window.location.href)
  url.protocol = url.protocol.replace('http', 'ws')
  console.log('Connecting WS', url.href)
  websock = new WebSocket(url.href)
  websock.onmessage = CallInfo.onMessageReceived
  websock.onopen = CallInfo.sendIdentification
}

CallInfo.sendIdentification = function () {
  var message = 'IDEN:' + Auth.username() + ':'
  websock.send(message)
}

CallInfo.onMessageReceived = function (event) {
  console.log('WS:', event.data)
  var message = event.data.split(':')
  var type_of_message = message[0]
  if (type_of_message === 'PHONE') {
    var phone = message[1]
    var date = message[2] + ':' + message[3] + ':' + message[4]
    CallInfo.callReceived(date, phone)
    CallInfo.retrievePersonCalls()
    return
  }
  if (type_of_message === 'REFRESH') {
    CallInfo.retrievePersonCalls()
    return
  }
  console.debug('Message received from WebSockets and type not recognized.')
}
CallInfo.emulateCall = function (phone, extension) {
  api
    .request({
      url: '/api/info/ringring',
      params: {
        extension: extension,
        phone: phone,
      },
    })
    .then(function (response) {
      console.log(`Call emulated from ${phone} to ${extension}`)
    })
}

CallInfo.getCategories()
CallInfo.retrievePersonCalls()

Auth.onLogin.subscribe(CallInfo.sendIdentification)
Auth.onLogin.subscribe(CallInfo.retrievePersonCalls)
Auth.onLogout.subscribe(CallInfo.sendIdentification)
Auth.onLogout.subscribe(CallInfo.retrievePersonCalls)
Auth.onUserChanged.subscribe(CallInfo.changeUser)
Auth.onUserChanged.subscribe(CallInfo.retrievePersonCalls)
connectWebSocket()

export default CallInfo

// vim: et ts=2 sw=2
