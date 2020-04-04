import $ from 'jquery'
import 'bootstrap/js/src/tooltip'
import { options as commonOptions, extractTemplateHtml } from './common'
import { init as paginatorInit } from './paginator'
import { add as usernameAdd } from './username'
import { add as timeActualizerAdd } from './time-actualizer'
import { add as popoverHovercontentAdd } from './popover-hovercontent'

class Instance {
  constructor(options) {
    this.options = options
  }

  initializePopoverContent(jqLink, jqTip) {
    const slug = jqLink.data('slug')
    const jqTipTemplate =
      this.jqRoot.find(`.forum-topic-tooltip-template[data-slug="${slug}"]`)
    const contentHtml = extractTemplateHtml(jqTipTemplate[0])
    jqTip.find('.popover-body').html(contentHtml)
  }

  onXhrSuccessLoadPage(html) {
    this.jqAjaxRequest = null
    this.jqWrappers.topicList.html(html)
    this.initUi()
  }

  onXhrErrorLoadPage() {
    this.jqAjaxRequest = null
  }

  loadPage(currentPageNo) {
    if (this.jqAjaxRequest) {
      // Abort the existing request
      this.jqAjaxRequest.abort()
      this.jqAjaxRequest = null
    }
    $.when(this.jqAjaxRequest = $.ajax({
      url: this.options.urls.topicListPage,
      data: {
        topic_type: this.options.topicType,
        page_id: currentPageNo,
      },
      dataType: 'html',
    })).then(::this.onXhrSuccessLoadPage, ::this.onXhrErrorLoadPage)
  }

  onXhrSuccessArchivedStart(html) {
    this.jqWrappers.loaderTopicsArchived.replaceWith(html)
    this.jqWrappers.topicList =
      this.jqRoot.find(this.options.selectors.topicListWrapper)
    delete this.jqWrappers.loaderTopicsArchived
    delete this.jqWrappers.buttonTopicsArchivedLoad
    this.initUi()
    this.focusOnHeader()
  }

  focusOnHeader() {
    $('html, body').animate({
      scrollTop: this.jqRoot.offset().top - commonOptions.navbarHeight,
    }, commonOptions.scrollSpeed)
  }

  /* eslint-disable class-methods-use-this, no-unused-vars */
  onXhrErrorArchivedStart(xhr) {
  }
  /* eslint-enable class-methods-use-this, no-unused-vars */

  onClickButtonTopicsArchivedLoad() {
    this.jqWrappers.buttonTopicsArchivedLoad
      .prop('disabled', true)
      .find('.fa')
      .removeClass()
      .addClass('fa fa-spinner fa-pulse fa-fw')
    $.when($.ajax({
      url: this.options.urls.archivedTopicsStart,
      dataType: 'html',
    })).then(::this.onXhrSuccessArchivedStart, ::this.onXhrErrorArchivedStart)
  }

  initUi() {
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    usernameAdd(jqUsers)
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizerAdd(jqTimeElements)
    const jqTopicLinkElements = this.jqRoot.find('.topic-link')
    for (const node of jqTopicLinkElements) {
      popoverHovercontentAdd(node, {
        clickTakeOver: false,
        groupName: 'topic-tooltips',
        callbacks: {
          contentInit: ::this.initializePopoverContent,
        },
        popover: {
          placement: 'auto',
        },
      })
    }
    this.jqWrappers.paginator =
      this.jqRoot.find(this.options.selectors.paginationWrapper)
    this.paginator = paginatorInit({
      jqRoot: this.jqWrappers.paginator.find(this.options.selectors.paginator),
      callbackLoadPage: ::this.loadPage,
    })
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqWrappers = {
      topicList: this.jqRoot.find(this.options.selectors.topicListWrapper),
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
  const instance = new Instance(options)
  $.when($.ready).then(::instance.initialize)
}
