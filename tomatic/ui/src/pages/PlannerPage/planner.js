import api from '../../services/api'
import messages from '../../services/messages'

function launch(params) {
  const context = 'Llençant una graella'
  return api
    .request({
      context,
      url: `/api/planner/api/run`,
      method: 'POST',
      params,
    })
    .then(
      (result) => {
        messages.success('ok', { context })
        return result
      },
      (error) => {
        messages.error('' + error, { context })
      },
    )
}

export default { launch }
