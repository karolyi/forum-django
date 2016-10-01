require('bootstrap/js/src/tooltip')
const $ = require('jquery')
const common = require('./common')
const paginator = require('./paginator')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')
const popOverHoverContent = require('./popOverHoverContent')

class Instance {
  constructor(options) {
    this.options = options
  }

  initializePopoverContent(jqLink, jqTip) {
    const slug = jqLink.data('slug')
    const jqTipTemplate =
      this.jqRoot.find(`.forum-topic-tooltip-template[data-slug="${slug}"]`)
    const contentHtml = common.extractTemplateHtml(jqTipTemplate[0])
    jqTip.find('.popover-content').empty().append(contentHtml)
  }

  activateContent() {
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
    const jqTopicLinkElements = this.jqRoot.find('.topic-link')
    for (const node of jqTopicLinkElements) {
      popOverHoverContent.add(node, {
        clickTakeOver: false,
        callbacks: {
          contentInit: ::this.initializePopoverContent,
        },
      })
    }
  }

  onXhrSuccessLoadPage(html) {
    this.jqAjaxRequest = null
    this.jqWrappers.topicList.html(html)
    this.activateContent()
    this.paginator.updateUi()
  }

  // onXhrErrorLoadPage(xhr) {
  onXhrErrorLoadPage() {
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

  onXhrSuccessArchivedStart(html) {
    const jqHtml = $(html)
    // IMPORTANT: keep the same class names in
    // topic-archived-start.html!
    this.jqWrappers.topicList.empty().append(
      jqHtml.filter(this.options.selectors.topicListWrapper).contents())
    const jqPaginationHtml =
      jqHtml.filter(this.options.selectors.paginationWrapper)
    this.options.pageMax = jqPaginationHtml.data('max-pages')
    this.jqWrappers.paginator.empty().append(jqPaginationHtml.contents())
    this.initUi()
    this.focusOnHeader()
  }

  focusOnHeader() {
    $('html, body').animate({
      scrollTop: this.jqRoot.offset().top - common.options.navbarHeight,
    }, common.options.scrollSpeed)
  }

  /* eslint-disable class-methods-use-this, no-unused-vars */
  onXhrErrorArchivedStart(xhr) {
  }
  /* eslint-enable class-methods-use-this, no-unused-vars */

  onClickButtonTopicsArchivedLoad() {
    this.jqWrappers.loaderTopicsArchived.remove()
    delete this.jqWrappers.loaderTopicsArchived
    delete this.jqWrappers.buttonTopicsArchivedLoad
    $.when($.ajax({
      url: this.options.urls.archivedTopicsStart,
      dataType: 'html',
    })).then(::this.onXhrSuccessArchivedStart, ::this.onXhrErrorArchivedStart)
  }

  initUi() {
    // Init paginator
    this.paginator = paginator.init({
      currentPageNr: 1,
      jqRoot: this.jqRoot.find(this.options.selectors.paginator),
      callbackLoadPage: ::this.loadPage,
      pageMax: this.options.pageMax,
    })
    this.activateContent()
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqWrappers = {
      topicList: this.jqRoot.find(this.options.selectors.topicListWrapper),
      paginator: this.jqRoot.find(this.options.selectors.paginationWrapper),
    }
    // Non archived or archived & shown topics will have a pageMax > 0
    if (this.options.pageMax > 0) {
      this.initUi()
      return
    }
    // topicType === 'archived', expandArchived === false
    this.jqWrappers.loaderTopicsArchived =
      this.jqRoot.find(this.options.selectors.loaderTopicsArchivedWrapper)
    this.jqWrappers.buttonTopicsArchivedLoad =
      this.jqRoot.find(this.options.selectors.buttonTopicsArchivedLoad)
    this.jqWrappers.buttonTopicsArchivedLoad
      .click(::this.onClickButtonTopicsArchivedLoad)
  }
}

export function init() {

}

export function add(options) {
  // Wait for document-ready
  $.when($.ready).then(() => {
    const instance = new Instance(options)
    instance.initialize()
  })
}
