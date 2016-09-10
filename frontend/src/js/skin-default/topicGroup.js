require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
const $ = require('jquery')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')
const paginator = require('./paginator')

class Instance {
  constructor(options) {
    this.options = options
  }

  activateContent() {
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

  onXhrSuccessLoadPage(html) {
    this.jqAjaxRequest = null
    this.jqWrappers.topicList.html(html)
    this.activateContent()
    this.paginator.updateUi()
  }

  onXhrErrorLoadPage(xhr) {
    this.jqAjaxRequest = null
  }

  loadPage(currentPageNr) {
    if (this.jqAjaxRequest) {
      // Abort the existing request
      this.jqAjaxRequest.abort()
      this.jqAjaxRequest = null
    }
    $.when(this.jqAjaxRequest = $.ajax({
      url: this.options.urls.topicListPage,
      data: {
        topic_type: this.options.topicType,
        page_id: currentPageNr,
      },
      dataType: 'html',
    // https://github.com/tc39/proposal-bind-operator
    })).then(::this.onXhrSuccessLoadPage, ::this.onXhrErrorLoadPage)
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqWrappers = {
      topicList: this.jqRoot.find(this.options.selectors.topicListWrapper),
    }
    // Init paginator
    this.paginator = paginator.init({
      currentPageNr: 1,
      jqRoot: this.jqRoot.find(this.options.selectors.paginator),
      callbackLoadPage: ::this.loadPage,
      pageMax: this.options.pageMax,
    })
    this.activateContent()
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
