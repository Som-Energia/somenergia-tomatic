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
function list() {
  const context = `Obtenint llistat d'execucions de graelles`
  return api
    .request({
      context,
      url: '/api/planner/api/list',
    })
    .then((results) => {
      return results.tasks
    })
    .catch((error) => {
      messages.error('' + error, { context })
    })
}
function taskCommand(task, command, context) {
  return api
    .request({
      context,
      url: `/api/planner/api/${command}/${task.name}`,
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

const planner = {
  launch,
  list,
  stop: (task) => taskCommand(task, 'stop', 'Parant la graella'),
  kill: (task) => taskCommand(task, 'kill', 'Matant la graela'),
  remove: (task) => taskCommand(task, 'remove', 'Esborrant la graela'),
  upload: (task) => taskCommand(task, 'upload', 'Pujant la graella'),
}

export default planner
