import api from '../../services/api'
import messages from '../../services/messages'

function launch(params) {
  const context = 'Llençant una graella'
  api
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

const planner = { launch }

export default planner
