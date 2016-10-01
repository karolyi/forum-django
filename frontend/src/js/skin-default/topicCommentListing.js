import { ScrollFix } from './scrollFix'

require('bootstrap/js/src/popover')
require('bootstrap/js/src/tooltip')
const $ = require('jquery')
const common = require('./common')
// const paginator = require('./paginator')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

class CommentListing {
  constructor(options) {
    this.options = options
  }

  constructUrlPath(commentId) {
    const urlTemplate = this.options.urls.commentListing
    return urlTemplate.backend
      .replace(urlTemplate.commentId, commentId)
      .replace(urlTemplate.exampleSlug, this.options.topicSlug)
  }

  /**
   * Look for the current visible comment, and change the current URL
   * to that, so the URL will reflect what comment is in focus
   * currently.
   */
  updateUrl() {
    const minY = common.options.navbarHeight + window.scrollY
    let jqTopComment
    for (const item of this.jqWrappers.comments) {
      const jqItem = $(item)
      if (jqItem.offset().top >= minY) {
        jqTopComment = jqItem
        break
      }
    }
    if (!jqTopComment) {
      // When this is reached, it means we're at the bottom at the page,
      // where the header of the bottom comment is not visible
      jqTopComment = this.jqWrappers.comments.last()
    }
    const topCommentId = jqTopComment.data('commentId')
    const constructedUrl = this.constructUrlPath(topCommentId)
    if (constructedUrl === location.pathname) return
    history.replaceState({}, null, constructedUrl)
  }

  getScrollToElement(commentId) {
    return this.jqWrappers.comments.filter(`[data-comment-id=${commentId}]`)
  }

  afterScrollTo(jqElement /* , isScrolled */) {
    // Flash the linked comment
    jqElement.addClass(this.options.highlightedClass)
    setTimeout(() => {
      jqElement.removeClass(this.options.highlightedClass)
    }, 100)
  }

  onClickCommentLink(event) {
    const previousCommentId = event.currentTarget.dataset.linkTo
    const jqExistingComment = this.getScrollToElement(previousCommentId)
    if (!jqExistingComment.length) {
      // The linked comment is not on this page
      return
    }
    event.preventDefault()
    history.pushState({}, null, event.currentTarget.href)
    this.scrollFix.scrollTo(previousCommentId)
  }

  onPopState() {
    const commentId = document.location.pathname.split('/')[3]
    if (!commentId) return
    this.scrollFix.scrollTo(commentId)
  }

  initializeCommentActionsContent(jqButton, jqTip) {
    if (jqTip.data('isInitialized')) return
    jqTip.data('isInitialized', true)
    jqButton.on('inserted.bs.popover', () => {
      const jqCommentWrapper =
        jqButton.parents(this.options.selectors.commentWrapper)
      const hasPreviousComment =
        !!jqCommentWrapper.has(this.options.selectors.previousLinks).length
      const hasAnswers =
        !!jqCommentWrapper.has(this.options.selectors.answerLinks).length
      const jqTemplate = this.jqTemplates.commentActions.clone()
      // Buttons are topmost in jqTemplate, hence .filter and not .find
      jqTemplate.filter(this.options.selectors.action.expandCommentsDown)
        .toggle(hasPreviousComment)
      jqTemplate.filter(this.options.selectors.action.expandCommentsUp)
        .toggle(hasAnswers)
      jqTip.find('.popover-content').empty().append(jqTemplate)
      jqTip.find('[data-toggle="tooltip"]').tooltip()
    })
  }

  static bindEventsToCommentActionsTip(jqButton, jqTip) {
    // Don't bind mouseleave/mouseenter events more than once
    if (jqTip.data('isAlreadyBound')) return
    jqTip.mouseleave(() => {
      CommentListing.onMouseLeaveCommentActionsTip(jqButton, jqTip)
    }).mouseenter(() => {
      CommentListing.onMouseEnterCommentActionsTip(jqButton, jqTip)
    })
    jqTip.data('isAlreadyBound', true)
  }

  static onMouseLeaveCommentActionsTip(jqButton, jqTip) {
    jqTip.data('isTipMouseEntered', false)
    setTimeout(() => {
      if (jqButton.data('isButtonMouseEntered')) return
      jqButton.popover('hide')
      jqTip.data('isShown', false)
    })
  }

  static onMouseEnterCommentActionsTip(jqButton, jqTip) {
    jqTip.data('isTipMouseEntered', true)
  }

  onMouseEnterCommentActionsButton(event) {
    const jqButton = $(event.currentTarget)
    jqButton.data('isButtonMouseEntered', true)
    const popOverInstance = jqButton.data('bs.popover')
    const jqTip = $(popOverInstance.getTipElement())
    if (!jqTip.data('isShown')) {
      this.initializeCommentActionsContent(jqButton, jqTip)
      jqTip.data('isShown', true)
      jqButton.popover('show')
    }
    CommentListing.bindEventsToCommentActionsTip(jqButton, jqTip)
  }

  static onMouseLeaveCommentActionsButton(event) {
    const jqButton = $(event.currentTarget)
    jqButton.data('isButtonMouseEntered', false)
    setTimeout(() => {
      const popOverInstance = jqButton.data('bs.popover')
      const jqTip = $(popOverInstance.getTipElement())
      if (jqTip.data('isTipMouseEntered')) return
      jqButton.popover('hide')
      jqTip.data('isShown', false)
    })
  }

  onClickCommentActionsButton(event) {
    const jqButton = $(event.currentTarget)
    const popOverInstance = jqButton.data('bs.popover')
    const jqTip = $(popOverInstance.getTipElement())
    if (!jqTip.data('isShown')) {
      this.initializeCommentActionsContent(jqButton, jqTip)
      jqButton.popover('show')
      jqTip.data('isShown', true)
    } else {
      jqButton.popover('hide')
      jqTip.data('isShown', false)
    }
    CommentListing.bindEventsToCommentActionsTip(jqButton, jqTip)
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqTemplates = {
      commentActions: $(common.extractTemplateHtml(
        this.jqRoot.find(this.options.selectors.template.action)[0])),
    }
    this.jqWrappers = {
      comments: this.jqRoot.find(this.options.selectors.commentWrapper),
    }
    this.jqWrappers.comments.find(this.options.selectors.previousLinks)
      .click(::this.onClickCommentLink)
    this.jqWrappers.comments.find(this.options.selectors.answerLinks)
      .click(::this.onClickCommentLink)
    this.jqWrappers.comments.find(this.options.selectors.selfLinks)
      .click(::this.onClickCommentLink)
    this.jqWrappers.comments.find(this.options.selectors.commentActions)
      .mouseenter(::this.onMouseEnterCommentActionsButton)
      .mouseleave(CommentListing.onMouseLeaveCommentActionsButton)
      .click(::this.onClickCommentActionsButton)
      .popover({
        trigger: 'manual',
      })
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
    $(window).on('popstate', ::this.onPopState)
    this.scrollFix = new ScrollFix({
      callbacks: {
        getScrollToElement: ::this.getScrollToElement,
        afterScrollTo: ::this.afterScrollTo,
        updateUrl: ::this.updateUrl,
      },
      scrollToInitial: this.options.scrollTo,
    })
    this.scrollFix.initialize()
  }
}

export function init(options) {
  $.when($.ready).then(() => {
    const commentListing = new CommentListing(options)
    commentListing.initialize()
  })
}
