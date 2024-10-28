// This module controls the state regarding the callinfo page
import api from '../services/api'
import Auth from '../services/auth'
import subscriptable from '../services/subscriptable'
import { prop as reactiveProp } from '../services/subscriptable'
import messages from '../services/messages'
import autofiltertype from '../services/autofiltertype'
//import dummy_categories from '../data/categories.yaml'

var websock = null
var CallInfo = {}

///// Auto refresh (the lock icon)

CallInfo.autoRefresh = reactiveProp(true)
CallInfo.autoRefresh.toggle = () => {
  CallInfo.autoRefresh(!CallInfo.autoRefresh())
}

///// Search params

CallInfo._search_query = {
  text: '',
  field: 'auto',
}
CallInfo.search_query = subscriptable((...args) => {
  if (args.length === 0) return CallInfo._search_query
  CallInfo._search_query = { ...CallInfo._search_query, ...args[0] }
  CallInfo.search_query.notify()
})

// Nicely clears search results
CallInfo.resetSearch = function () {
  CallInfo.selectPartner(0)
  CallInfo.results({})
}

CallInfo.searchCustomer = function () {
  CallInfo.resetSearch()
  if (CallInfo.search_query().text === '') return
  retrieveInfo()
}

CallInfo.handleUserChanged = function (newUser) {
  CallInfo.deselectLog()
  CallInfo.personCalls([])
  CallInfo.autoRefresh(true)
  CallInfo.retrievePersonCalls()
}

CallInfo.callReceived = function (date, phone, call_id) {
  if (!CallInfo.autoRefresh()) {
    return
  }
  CallInfo.selectLog(date, phone, call_id)
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

function fixContractNumbersInCallLog(response) {
  response.calls.forEach(function (call) {
    if (!call.contract_number) return
    call.contract_number = formatContractNumber(call.contract_number)
  })
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

///// Person and Contract tabs status

CallInfo.currentPerson = 0 // Selected person from search data
CallInfo.currentContract = 0 // Selected contract selected person

CallInfo.selectedPartner = subscriptable(function () {
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
})

CallInfo.selectedContract = subscriptable(function () {
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
})

CallInfo.selectContract = function (idx) {
  CallInfo.currentContract = idx
  CallInfo.selectedContract.notify()
}

CallInfo.selectPartner = function (idx) {
  CallInfo.currentPerson = idx
  CallInfo.currentContract = 0
  CallInfo.selectedPartner.notify()
  CallInfo.selectedContract.notify()
}

///// Search results

CallInfo.results = reactiveProp({})
CallInfo.loadingDetails = reactiveProp(false)

var retrieveInfo = function () {
  CallInfo.results({ 1: 'empty' }) // Searching...
  const searchValue = CallInfo.search_query().text.trim()
  let searchField = CallInfo.search_query().field
  if (searchField === 'auto') searchField = autofiltertype(searchValue) || 'all'
  const encodedValue = encodeURIComponent(searchValue)
  const context = 'Cercant dades de la usuaria'
  function exitWithError(msg) {
    messages.error(msg, { context })
    CallInfo.results({ 1: 'error' })
  }

  api
    .request({
      context,
      url: '/api/info/' + searchField + '/' + encodedValue,
    })
    .then(
      function (response) {
        console.debug('Info GET Response: ', response)
        if (!response) {
          CallInfo.results({ 1: 'error' })
          return
        }
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
        // Keep the context, just in case a second query is started
        // and CallInfo.results() is overwritten
        var contextResults = CallInfo.results()
        CallInfo.loadingDetails(true)
        api
          .request({
            context,
            method: 'POST',
            url: '/api/info/contractdetails',
            body: {
              contracts: contractNumbers(contextResults),
            },
          })
          .then(fixContractNumbersInDetails)
          .then(function (response) {
            contextResults.partners.forEach(function (partner) {
              partner.contracts.forEach(function (contract) {
                var number = formatContractNumber(contract.number)
                var retrieved = response.info.info[number]
                if (retrieved === undefined) return
                contract.invoices = retrieved.invoices
                contract.lectures_comptadors = retrieved.lectures_comptadors
                contract.atr_cases = retrieved.atr_cases
              })
            })
            CallInfo.loadingDetails(false)
          })
      },
      function (error) {
        return exitWithError('Info GET apicall failed: ' + error)
      },
    )
}

///// Usage instrumentation

CallInfo.notifyUsage = function (event) {
  const context = 'Registrant ús'
  api.request({
    context,
    method: 'POST',
    url: '/api/logger/' + event,
    body: {
      user: Auth.username(),
    },
  })
}

///// Call categories

CallInfo.categories = reactiveProp([])
CallInfo.retrieveCategories = function () {
  const context = 'Obtenint categories de tipificació'
  api
    .request({
      context,
      url: '/api/call/categories',
    })
    .then(
      function (response) {
        console.debug('Categories GET Response: ', response)

        if (!response) return
        // TODO: Take them from the API
        CallInfo.categories(response.categories)
        //CallInfo.categories(dummy_categories.categories)
      },
      function (error) {
        console.debug('Info GET apicall failed: ', error)
      },
    )
}

///// Call log

CallInfo.personCalls = reactiveProp([]) // User call registry

CallInfo.retrievePersonCalls = function () {
  const context = 'Obtening les trucades ateses'
  var username = Auth.username()
  if (username === -1 || username === '') {
    CallInfo.personCalls([])
    return 0
  }
  CallInfo.personCalls(undefined) // Loading
  api
    .request({
      context,
      url: '/api/call/log',
    })
    .then(function (response) {
      if (!response) return
      fixContractNumbersInCallLog(response)
      console.debug('Info GET Response: ', response)
      CallInfo.personCalls(response.calls)
    })
}

CallInfo.savingAnnotation = false
CallInfo.modifyCall = function (call) {
  const context = 'Tipificant la trucada'
  CallInfo.savingAnnotation = true
  api
    .request({
      method: call.id ? 'PUT' : 'POST',
      url: 'api/call/annotate',
      body: { ...call, id: call.id || undefined },
    })
    .then(
      function (response) {
        if (!response) {
          CallInfo.savingAnnotation = false
          return
        }
        fixContractNumbersInCallLog(response)
        CallInfo.savingAnnotation = false
        messages.success('Anotació desada', { context })
        CallInfo.deselectLog()
        CallInfo.personCalls(response.calls)
      },
      function (error) {
        CallInfo.savingAnnotation = false
        messages.error(error + '', { context })
      },
    )
}

CallInfo.deleteAnnotation = function (call) {
  const context = 'Esborrant la anotació'
  CallInfo.savingAnnotation = true
  api
    .request({
      method: 'PUT',
      url: 'api/call/annotate',
      body: {
        ...call,
        comments: '',
        category_ids: [],
        caller_erp_id: null,
        caller_vat: '',
        caller_name: '',
        contract_erp_id: null,
        contract_number: '',
        contract_address: '',
      },
    })
    .then(
      function (response) {
        CallInfo.savingAnnotation = false
        messages.success('Anotació esborrada', { context })
        CallInfo.deselectLog()
        CallInfo.personCalls(response.calls)
      },
      function (error) {
        CallInfo.savingAnnotation = false
        messages.error(error + '', { context })
      },
    )
}

CallInfo.currentCall = reactiveProp(null)

CallInfo.isLogSelected = function (call_id) {
  return CallInfo.currentCall() === call_id
}

CallInfo.selectLog = function (date, phone, call_id) {
  CallInfo.resetSearch()
  CallInfo.search_query({
    text: phone,
    field: 'auto',
  })
  CallInfo.currentCall(call_id)
  retrieveInfo()
}

CallInfo.deselectLog = function () {
  CallInfo.resetSearch()
  CallInfo.search_query({ text: '' })
  CallInfo.currentCall(null)
}

CallInfo.toggleLog = function (date, phone, call_id) {
  if (CallInfo.isLogSelected(call_id)) {
    CallInfo.deselectLog()
  } else {
    CallInfo.selectLog(date, phone, call_id)
  }
}

CallInfo.callData = function (call_id) {
  const context = `Cercant dades per la trucada ${call_id}`
  if (!call_id) return
  for (const call of CallInfo.personCalls() || []) {
    if (call.id === call_id) {
      return call
    }
  }
  messages.warning("No s'ha trobat", { context })
}

///// Web Sockets

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
  const message = JSON.parse(event.data)
  if (message.type === 'PHONE') {
    CallInfo.callReceived(message.date, message.phone, message.call_id)
    CallInfo.retrievePersonCalls()
    return
  }
  if (message.type === 'REFRESH') {
    CallInfo.retrievePersonCalls()
    return
  }
  console.debug('Message received from WebSockets and type not recognized.')
}
CallInfo.emulateCall = function (phone, extension) {
  api
    .request({
      url: '/api/info/ringring?',
      params: {
        extension: extension,
        phone: phone,
      },
    })
    .then(function (response) {
      console.log(`Call emulated from ${phone} to ${extension}`)
    })
}

///// Global Initialization

CallInfo.retrieveCategories()
CallInfo.retrievePersonCalls()

// TODO: Put some order here
Auth.onLogin.subscribe(CallInfo.sendIdentification)
Auth.onLogin.subscribe(CallInfo.retrievePersonCalls)
Auth.onLogout.subscribe(CallInfo.sendIdentification)
Auth.onLogout.subscribe(CallInfo.retrievePersonCalls)
Auth.onUserChanged.subscribe(CallInfo.handleUserChanged)
// TODO: Avoid development reload is creating a new connection on every edit
connectWebSocket()

export default CallInfo

// vim: et ts=2 sw=2
