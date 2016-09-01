const mutationObserver = require('./mutationObserver')

class Instance {
  constructor(options) {
    this.options = options
    this.elements = []
  }

  removeCallback(targetNode) {
    console.log('removed', targetNode, this.options)
  }

  initialize() {
    mutationObserver.observeRemove(
      this.options.jqUsers, this.removeCallback.bind(this))
  }
}

export function init(options) {
  const instance = new Instance(options)
  instance.initialize()
}
