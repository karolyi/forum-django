const $ = require('jquery')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
  }
}

export function init(options) {

}

export function add(options) {
  // Wait for document-ready
  $.when($.ready).then(() => {
    const instance = new Instance(options)
    instance.initialize()
  })
}
