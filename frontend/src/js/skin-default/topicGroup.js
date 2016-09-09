require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
const $ = require('jquery')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

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
    this.jqWrappers.paginator
      .find('.page-numbered.active').removeClass('active')
    this.jqWrappers.paginator
      .find(`.page-numbered[data-page-id=${this.currentPageNr}]`)
      .addClass('active')
    this.jqWrappers.pagePreviousLink.parent()
      .toggleClass('disabled', this.currentPageNr < 2)
    this.jqWrappers.pageNextLink.parent()
      .toggleClass('disabled', this.currentPageNr > this.options.pageMax - 1)
  }

  onXhrErrorLoadPage(xhr) {
    this.jqAjaxRequest = null
  }

  onClickPaginatePrevious(event) {
    event.preventDefault()
    if (this.currentPageNr <= 1) return
    this.currentPageNr--
    this.loadPage()
  }

  onClickPaginateNext(event) {
    event.preventDefault()
    if (this.currentPageNr >= this.options.pageMax) return
    this.currentPageNr++
    this.loadPage()
  }

  onClickPaginateNumber(event) {
    event.preventDefault()
    const parentElement = event.currentTarget.parentElement
    if (parentElement.classList.contains('active')) return
    this.currentPageNr =
      parseInt(parentElement.dataset.pageId, 10)
    if (this.currentPageNr > this.options.pageMax || this.currentPageNr < 1) {
      this.currentPageNr = 1
    }
    this.loadPage()
  }

  loadPage() {
    if (this.jqAjaxRequest) {
      // Abort the existing request
      this.jqAjaxRequest.abort()
      this.jqAjaxRequest = null
    }
    $.when(this.jqAjaxRequest = $.ajax({
      url: this.options.urls.topicListPage,
      data: {
        topic_type: this.options.topicType,
        page_id: this.currentPageNr,
      },
      dataType: 'html',
    // https://github.com/tc39/proposal-bind-operator
    })).then(::this.onXhrSuccessLoadPage, ::this.onXhrErrorLoadPage)
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqWrappers = {
      topicList: this.jqRoot.find(this.options.selectors.topicListWrapper),
      paginator: this.jqRoot.find(this.options.selectors.paginator),
    }
    this.jqWrappers.pageNextLink =
      this.jqWrappers.paginator.find('.page-next a')
    this.jqWrappers.pagePreviousLink =
      this.jqWrappers.paginator.find('.page-previous a')
    this.currentPageNr = 1
    this.activateContent()
    // Init paginator
    this.jqWrappers.pagePreviousLink.click(::this.onClickPaginatePrevious)
    this.jqWrappers.pageNextLink.click(::this.onClickPaginateNext)
    this.jqWrappers.paginator.find('.page-numbered a')
      .click(::this.onClickPaginateNumber)
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
