/* global interpolate */
import { ScrollFix } from './scrollFix'

require('bootstrap/js/src/tooltip')
const popOverHoverContent = require('./popOverHoverContent')
const $ = require('jquery')
const common = require('./common')
// const paginator = require('./paginator')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

export class CommentListing {
  constructor(options) {
    this.options = options
  }

  prepareUrlFormatStrings() {
    this.urlFormatStrings = {
      commentListing: this.options.urls.commentListing.backend
        .replace(this.options.urls.commentListing.exampleSlug, '%(topicSlug)s')
        .replace(this.options.urls.commentListing.commentId, '%(commentId)s'),
      expandCommentsUpRecursive:
        this.options.urls.expandCommentsUpRecursive.backend
        .replace(
          this.options.urls.expandCommentsUpRecursive.exampleSlug,
          '%(topicSlug)s')
        .replace(
          this.options.urls.expandCommentsUpRecursive.commentId,
          '%(commentId)s')
        .replace(
          this.options.urls.expandCommentsUpRecursive.scrollToId,
          '%(scrollToId)s'),
    }
  }

  constructPathFromData(topicSlug, commentId, scrollToIdPassed = null) {
    let scrollToId = scrollToIdPassed
    if (!scrollToIdPassed) scrollToId = commentId
    const formatString = this.urlFormatStrings[this.options.listingMode]
    return interpolate(formatString, {
      topicSlug,
      commentId,
      scrollToId,
    }, true)
  }

  constructPathFromWrapper(jqCommentWrapper) {
    const commentId = jqCommentWrapper.data('commentId')
    const topicSlug = this.options.topicSlugOriginal
    return this.constructPathFromData(topicSlug, commentId)
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
    const constructedPath = this.constructPathFromWrapper(jqTopComment)
    if (constructedPath === location.pathname) return
    history.replaceState({}, null, constructedPath)
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

  sendBrowserToComment(event) {
    const commentIdLinked = event.currentTarget.dataset.linkTo
    const jqExistingComment = this.getScrollToElement(commentIdLinked)
    if (!jqExistingComment.length) {
      // The linked comment is not on this page, send the browser to the
      // link
      return
    }
    event.preventDefault()
    // Construct the pushed URL
    const constructedPath = this.constructPathFromData(
      this.options.topicSlugOriginal, commentIdLinked)
    history.pushState({}, null, constructedPath)
    this.scrollFix.scrollTo(commentIdLinked)
  }

  onClickLinkPreviousComment(event) {
    this.sendBrowserToComment(event)
  }

  onClickLinkReplyComment(event) {
    this.sendBrowserToComment(event)
  }

  onClickLinkComment(event) {
    if (this.options.listingMode !== 'commentListing') {
      // The listing mode is not the topic comment listing page, so we
      // send the browser to the topic comment listing page.
      return
    }
    this.sendBrowserToComment(event)
  }

  onClickButtonExpandCommentsUpRecursive(jqCommentWrapper) {
    const commentId = jqCommentWrapper.data('commentId')
    const topicSlug = jqCommentWrapper.data('topicSlug')
    const constructedPath = interpolate(
      this.urlFormatStrings.expandCommentsUpRecursive, {
        commentId,
        topicSlug,
        scrollToId: commentId,
      }, true)
    if (constructedPath === location.pathname) return
    // Load the constructed url
    document.location.href = constructedPath
  }

  onPopState() {
    const commentId = document.location.pathname.split('/')[3]
    if (!commentId) return
    this.scrollFix.scrollTo(commentId)
  }

  initializeCommentActionsContent(jqButton, jqTip) {
    const jqCommentWrapper =
      jqButton.parents(this.options.selectors.commentWrapper)
    const hasPreviousComment =
      !!jqCommentWrapper.has(this.options.selectors.previousLinks).length
    const hasAnswers =
      !!jqCommentWrapper.has(this.options.selectors.replyLinks).length
    const jqTemplate = this.jqTemplates.commentActions.clone()
    // Buttons are topmost in jqTemplate, hence .filter and not .find
    const jqButtonExpandCommentsDown =
      jqTemplate.filter(this.options.selectors.action.expandCommentsDown)
    jqButtonExpandCommentsDown.toggle(hasPreviousComment)
    const jqButtonExpandCommentsUp =
      jqTemplate.filter(this.options.selectors.action.expandCommentsUp)
    jqButtonExpandCommentsUp.toggle(hasAnswers)
    const jqButtonExpandCommentsUpRecursive =
      jqTemplate.filter(this.options.selectors.action.expandCommentsUpRecursive)
    jqButtonExpandCommentsUpRecursive.toggle(hasAnswers)
    if (hasAnswers) {
      jqButtonExpandCommentsUpRecursive.click(() => {
        this.onClickButtonExpandCommentsUpRecursive(jqCommentWrapper)
      })
    }
    jqTip.find('.popover-content').empty().append(jqTemplate)
    jqTip.find('[data-toggle="tooltip"]').tooltip()
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.prepareUrlFormatStrings()
    this.jqTemplates = {
      commentActions: $(common.extractTemplateHtml(
        this.jqRoot.find(this.options.selectors.template.action)[0])),
    }
    this.jqWrappers = {
      comments: this.jqRoot.find(this.options.selectors.commentWrapper),
    }
    this.jqWrappers.comments.find(this.options.selectors.previousLinks)
      .click(::this.onClickLinkPreviousComment)
    this.jqWrappers.comments.find(this.options.selectors.replyLinks)
      .click(::this.onClickLinkReplyComment)
    this.jqWrappers.comments.find(this.options.selectors.selfLinks)
      .click(::this.onClickLinkComment)
    const jqButtonCommentActions =
      this.jqWrappers.comments.find(this.options.selectors.commentActions)
    for (const button of jqButtonCommentActions) {
      popOverHoverContent.add(button, {
        clickTakeOver: true,
        callbacks: {
          contentInit: ::this.initializeCommentActionsContent,
        },
      })
    }
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
    $(window).on('popstate', ::this.onPopState)
    console.debug('scrolling init', this.options.scrollToId);
    this.scrollFix = new ScrollFix({
      callbacks: {
        getScrollToElement: ::this.getScrollToElement,
        afterScrollTo: ::this.afterScrollTo,
        updateUrl: ::this.updateUrl,
      },
      scrollToInitial: this.options.scrollToId,
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
