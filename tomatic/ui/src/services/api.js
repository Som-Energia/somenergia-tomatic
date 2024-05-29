import jsyaml from 'js-yaml'
import Auth from './auth'
import messages from './messages'

const debugApi = true
//const apiPrefix = 'http://localhost:4555'
const apiPrefix = ''

const api = {}
api.request = ({ context, url, params, body, headers, ...options }) => {
  const method = options.method || 'GET'
  const fullUrl = apiPrefix + url + new URLSearchParams(params)
  debugApi &&
    console.log(
      method,
      fullUrl,
      'Launched',
      options.params || options.body || '',
    )
  return fetch(fullUrl, {
    mode: 'same-origin',
    redirect: 'error',
    headers: {
      authorization: 'Bearer ' + Auth.token(),
      'content-type': 'application/x-yaml',
      ...headers,
    },
    body: body ? jsyaml.dump(body) : undefined,
    ...options,
  })
    .then(function (response) {
      console.log(response)
      if (!response.ok) throw response
      return response
    })
    .then(async function (response) {
      const text = await response.text()
        return jsyaml.load(text)
    })
    .then(function (result) {
      debugApi && console.log(method, fullUrl, 'Received', result)
      return result
    })
    .catch(function (error) {
      debugApi && console.log(method, fullUrl, 'Error', error)
      // Forbidden
      if (error.status === 403) {
        messages.error('Operació no permesa', { context })
        return undefined
      }
      // Unauthorized
      if (error.status === 401) {
        Auth.logout()
        return undefined
      }
      console.log("Que la tiro")
      throw error
    })
}

export default api

// vim: et ts=2 sw=2
