import jsyaml from 'js-yaml'
import Auth from './auth'
import messages from './messages'

const debugApi = true
//const apiPrefix = 'http://localhost:4555'
//const apiPrefix = 'https://tomatic.somenergia.coop'
const apiPrefix = ''

// Response/Error handling functions

function handleNetworkProblem(context) {
  return function (error) {
    console.error(context, error)
    messages.error('API error: ' + error, { context })
    return undefined
  }
}

function deserializeResponse(context) {
  return async function (response) {
    if (response === undefined) return undefined
    const text = await response.text()
    try {
      return jsyaml.load(text)
    } catch (error) {
      messages.warn('API YAML format error: ' + error, { context })
    }
    return text
  }
}

function handleHttpErrors(context) {
  return async function (response) {
    if (!response) return response
    if (response.ok) return response
    // Forbidden
    if (response.status === 403) {
      messages.error('Operació no permesa', { context })
      return undefined
    }
    // Unauthorized
    if (response.status === 401) {
      Auth.logout()
      return undefined
    }
    // TODO: Not working yet
    if (response.status === 302 || response.type === 'opaqueredirect') {
      messages.error('Tens desactivada la VPN!', { context })
      return undefined
    }
    messages.error(
      `Error inesperat ${response.status} ${
        response.statusText
      }\n${await response.text()}`,
      { context },
    )
    console.error(response)
    return
  }
}

const api = {}
api.request = ({ context, url, params, body, headers, ...options }) => {
  const method = options.method || 'GET'
  const fullUrl = apiPrefix + url + (params ? '?' + new URLSearchParams(params) : '')
  debugApi &&
    console.log(
      method,
      fullUrl,
      'Launched',
      options.params || options.body || '',
    )
  return fetch(fullUrl, {
    mode: 'same-origin',
    redirect: 'manual',
    headers: {
      authorization: 'Bearer ' + Auth.token(),
      'content-type': 'application/x-yaml',
      ...headers,
    },
    body: body ? jsyaml.dump(body) : undefined,
    ...options,
  })
    .catch(handleNetworkProblem(context))
    .then(handleHttpErrors(context))
    .then(deserializeResponse(context))
}

export default api

// vim: et ts=2 sw=2
