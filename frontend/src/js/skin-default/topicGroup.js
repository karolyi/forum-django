const $ = require('jquery')
// const bootstrap = require('bootstrap-sass')

class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    console.debug('jqRoot', this.jqRoot)
    // this.jqRoot.tooltip()
  }
}

export function init(options) {
  // Wait for document-ready
  $.when($.ready).then(() => {
    const instance = new Instance(options)
    instance.initialize()
  })
}
