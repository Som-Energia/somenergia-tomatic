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
					options.params || options.body || ''
				)
			return m
				.request(options)
				.then(function (result) {
					debugApi &&
						console.log(
							options.method || 'GET',
							options.url,
							'Received',
							result
						)
					return result
				})
				.catch(function (error) {
					debugApi &&
						console.log(
							options.method || 'GET',
							options.url,
							'Error',
							error
						)
					if (error.code !== 401) throw error
					// Unauthorized
					Auth.logout()
				})
		},

		deserialize: function (responseText) {
			return jsyaml.load(responseText)
		},
	}

	export default api
// vim: noet ts=4 sw=4
