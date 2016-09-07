require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
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
    const jqTopicLinkElements = this.jqRoot.find('.topic-link')
    for (let idx = 0; idx < jqTopicLinkElements.length; idx++) {
      const jqItem = $(jqTopicLinkElements[idx])
      const slug = jqItem.data('slug')
      const jqTooltip =
        this.jqRoot.find(`.forum-topic-tooltip-template[data-slug="${slug}"]`)
      jqItem.attr('title', jqTooltip.html())
    }
    jqTopicLinkElements.tooltip({
      html: true,
    })
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
