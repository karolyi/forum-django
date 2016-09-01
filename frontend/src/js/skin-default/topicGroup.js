const $ = require('jquery')
require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')

class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqRoot.find('[data-toggle=tooltip]').tooltip()
  }
}

export function init(options) {
  // Wait for document-ready
  $.when($.ready).then(() => {
    const instance = new Instance(options)
    instance.initialize()
  })
}
