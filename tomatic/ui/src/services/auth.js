module.exports = (function () {
  var subscriptable = require('./subscriptable').default
  var parseJwt = require('./utils').parseJwt

  const Auth = {}
  var previousLogin = null // To detect login changes

  Auth.token = function (value) {
    if (value) {
      localStorage.setItem('token', value)
    }
    return localStorage.getItem('token')
  }

  Auth.clearToken = function () {
    localStorage.removeItem('token')
  }

  Auth.userinfo = function () {
    const token = Auth.token()
    if (!token) return undefined
    const content = parseJwt(token)
    return content
  }

  Auth.error = function (value) {
    if (value !== undefined) {
      localStorage.setItem('autherror', value)
    }
    return localStorage.getItem('autherror')
  }

  Auth.loginWatchTimer = 0
  Auth.watchLoginChanges = function () {
    clearTimeout(Auth.loginWatchTimer)
    var user = Auth.username()
    if (user !== previousLogin) {
      console.log('Detected login change', previousLogin, '->', user)
      previousLogin = user
      Auth.login()
      Auth.onUserChanged.notify()
    }
    Auth.loginWatchTimer = setTimeout(Auth.watchLoginChanges, 500)
  }

  Auth.onLogout = subscriptable({})
  Auth.onLogin = subscriptable({})
  Auth.onUserChanged = subscriptable({})

  Auth.logout = function () {
    Auth.clearToken()
    Auth.onLogout.notify()
  }

  // TODO: Call this!
  Auth.login = function () {
    Auth.onLogin.notify()
  }

  Auth.username = function () {
    return Auth.userinfo()?.username || ''
  }

  Auth.authenticate = function () {
    window.location.href = '/api/auth/login'
  }

  Auth.watchLoginChanges()

  return Auth
})()

// vim: et ts=2 sw=2
