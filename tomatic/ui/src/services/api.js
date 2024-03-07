import m from 'mithril'
import jsyaml from 'js-yaml'
import Auth from './auth'

const debugApi = true
//const apiPrefix = 'http://localhost:4555'
const apiPrefix = ''

var api = {
  request: function (options) {
    options = { ...options }
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
