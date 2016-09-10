const $ = require('jquery')
const common = require('./common')
const paginator = require('./paginator')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

class CommentListing {
  constructor(options) {
    this.options = options
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqTemplates = {

    }
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
  }
}


export function init(options) {
  $.when($.ready).then(() => {
    const commentListing = new CommentListing(options)
    commentListing.initialize()
  })
}
