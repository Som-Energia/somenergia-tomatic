import m from 'mithril'
import jsyaml from 'js-yaml'
import Auth from './auth'
import messages from './messages'

const debugApi = false
//const apiPrefix = 'http://localhost:4555'
const apiPrefix = ''

var api = {
  request: function (options) {
    options = { ...options }
    const { context } = options
    options.config = function (xhr) {
      xhr.setRequestHeader('Authorization', 'Bearer ' + Auth.token())
    }
    options.responseType = 'yaml' // whatever different of json indeed
    options.deserialize = api.deserialize
    options.url = apiPrefix + options.url
    debugApi &&
      console.log(
        options.method || 'GET',
        options.url,
        'Launched',
        options.params || options.body || '',
      )
    return m
      .request(options)
      .then(function (result) {
        debugApi &&
          console.log(options.method || 'GET', options.url, 'Received', result)
        return result
      })
      .catch(function (error) {
        debugApi &&
          console.log(options.method || 'GET', options.url, 'Error', error)
        // Forbidden
        if (error.code === 403) {
          messages.error('Operació no permesa', { context })
          return undefined
        }
        // Unauthorized
        if (error.code === 401) {
          Auth.logout()
          return undefined
        }
        throw error
      })
  },

  deserialize: function (responseText) {
    return jsyaml.load(responseText)
  },
}
// vim: et ts=2 sw=2

export default api
// vim: et ts=2 sw=2
