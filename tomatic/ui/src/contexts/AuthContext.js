import * as React from 'react'
import Auth from '../services/auth'
import Tomatic from '../services/tomatic'

var updateUser = null
Auth.onUserChanged.push(() => updateUser && updateUser())
Tomatic.onPersonsUpdated.push(() => updateUser && updateUser())
Tomatic.onForcedTurnsUpdated.push(() => updateUser && updateUser())

function refreshedAuthUser() {
  const userid = Auth.username()
  return {
    userid,
    fullname: Tomatic.formatName(userid),
    initials: Tomatic.nameInitials(userid),
    color: '#' + Tomatic.personColor(userid),
    avatar: null,
  }
}

const AuthContext = React.createContext({})

function AuthProvider({ children }) {
  const [authUser, setAuthUser] = React.useState(refreshedAuthUser())
  updateUser = () => setAuthUser(refreshedAuthUser())
  return (
    <AuthContext.Provider value={authUser}>{children}</AuthContext.Provider>
  )
}

export { AuthProvider, AuthContext }
export default AuthContext
