module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var api = {

	request: function(options) {
		options.config = function(xhr) {
			xhr.setRequestHeader('Authorization', 'Bearer ' + api.token())
		};
		options.responseType = 'yaml'; // whatever different of json indeed
		options.deserialize = api.deserialize;
		console.log(options.method || 'GET', options.url, "Launched", options.params || options.body || '');
		return m.request(options).then(function(result) {
				console.log(options.method || 'GET', options.url, "Received", result);
				return result;
			}).catch(function(error) {
				console.log(options.method || 'GET', options.url, "Error", error);
				if (error.code !== 401) throw error;
				// Unauthorized
				location.href = '/api/auth/login'
			})
		;
	},

	token: function(value) {
		if (value) {
			localStorage.setItem('token', value);
		}
		return localStorage.getItem('token')
	},

	clearToken: function() {
		localStorage.removeItem('token')
	},

	deserialize: function(responseText) {
		return jsyaml.safeLoad(responseText);
	},
};

return api;

}();

// vim: noet ts=4 sw=4