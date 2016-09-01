// require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
const $ = require('jquery')
const userName = require('./userName')

class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.init({
      jqUsers,
    })
  }
}

export function init(options) {
  // Wait for document-ready
  $.when($.ready).then(() => {
    const instance = new Instance(options)
    instance.initialize()
  })
}
