require('bootstrap/js/src/tooltip')
const $ = require('jquery')
require('select2')
// const common = require('./common')
// const paginator = require('./paginator')
// const userName = require('./userName')
// const timeActualizer = require('./timeActualizer')
// const popOverHoverContent = require('./popOverHoverContent')

export class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    console.debug('initialize', this.options)
    $('#id_ignored_users').select2()
  }
}

export function init(options) {
  const settingsPage = new Instance(options)
  settingsPage.initialize()
  return settingsPage
}
