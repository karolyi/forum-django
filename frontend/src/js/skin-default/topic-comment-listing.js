import $ from 'jquery'
import template from 'lodash/template'
import { ScrollFix } from './scroll-fix'
import { options as commonOptions, extractTemplateHtml } from './common'
import { add as popoverHovercontentAdd } from './popover-hovercontent'
import { add as usernameAdd } from './username'
import { add as timeActualizerAdd } from './time-actualizer'
import { init as paginatorInit } from './paginator'

require('bootstrap/js/src/tooltip')

export class CommentListing {
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

  onMouseEnterLinkPreviousComment(event) {
    const commentIdLinked = event.currentTarget.dataset.linkTo
    this.highlightCommentId(commentIdLinked)
  }

  onMouseLeaveLinkPreviousComment(event) {
    const commentIdLinked = event.currentTarget.dataset.linkTo
    this.deHighlightCommentId(commentIdLinked)
  }

  onMouseEnterLinkReplyComment(event) {
    const commentIdLinked = event.currentTarget.dataset.linkTo
    this.highlightCommentId(commentIdLinked)
  }

  onMouseLeaveLinkReplyComment(event) {
    const commentIdLinked = event.currentTarget.dataset.linkTo
    this.deHighlightCommentId(commentIdLinked)
  }

  onPopState() {
    const commentId = document.location.pathname.split('/')[3]
    if (!commentId) return
    this.scrollFix.scrollTo(commentId)
  }

  onClickLoadPage(pageNo) {
    document.location.href = this.urls.commentListingPageNo({
      topicSlug: this.options.topicSlugOriginal, pageId: pageNo,
    })
  }

  constructor(options) {
    this.options = options
  }

  prepareUrlFormatStrings() {
    const { urls } = this.options
    this.urls = {
      commentListing: template(
        urls.commentListing.backend
          .replace(urls.commentListing.exampleSlug, '{topicSlug}')
          .replace(urls.commentListing.commentId, '{commentId}'),
      ),
      expandCommentsUpRecursive: template(
        urls.expandCommentsUpRecursive.backend
          .replace(urls.expandCommentsUpRecursive.exampleSlug, '{topicSlug}')
          .replace(urls.expandCommentsUpRecursive.commentId, '{commentId}')
          .replace(urls.expandCommentsUpRecursive.scrollToId, '{scrollToId}'),
      ),
      expandCommentsUp: template(
        urls.expandCommentsUp.backend
          .replace(urls.expandCommentsUp.exampleSlug, '{topicSlug}')
          .replace(urls.expandCommentsUp.commentId, '{commentId}')
          .replace(urls.expandCommentsUp.scrollToId, '{scrollToId}'),
      ),
      expandCommentsDown: template(
        urls.expandCommentsUp.backend
          .replace(urls.expandCommentsUp.exampleSlug, '{topicSlug}')
          .replace(urls.expandCommentsUp.commentId, '{commentId}')
          .replace(urls.expandCommentsUp.scrollToId, '{scrollToId}'),
      ),
    }
    if (this.options.listingMode === 'commentListing') {
      this.urls.commentListingPageNo = template(
        urls.commentListingPageNo.backend
          .replace(urls.commentListingPageNo.exampleSlug, '{topicSlug}')
          .replace(urls.commentListingPageNo.pageId, '{pageId}'),
      )
    }
  }

  constructPathFromData(topicSlug, commentId, scrollToIdPassed = null) {
    let scrollToId = scrollToIdPassed
    if (!scrollToIdPassed) scrollToId = commentId
    const formatString = this.urls[this.options.listingMode]
    return formatString({
      topicSlug,
      commentId,
      scrollToId,
    })
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
    const minY = commonOptions.navbarHeight + window.scrollY
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
    if (constructedPath === window.location.pathname) return
    window.history.replaceState({}, null, constructedPath)
  }

  getCommentWrapper(commentId) {
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
    const jqExistingComment = this.getCommentWrapper(commentIdLinked)

    if (!jqExistingComment.length) {
      // The linked comment is not on this page, send the browser to the
      // link
      return
    }
    event.preventDefault()
    // Construct the pushed URL
    const constructedPath = this.constructPathFromData(
      this.options.topicSlugOriginal, commentIdLinked,
    )
    window.history.pushState({}, null, constructedPath)
    this.scrollFix.scrollTo(commentIdLinked)
  }

  highlightCommentId(commentId) {
    const jqCommentWrapper = this.getCommentWrapper(commentId)
    jqCommentWrapper.addClass(this.options.highlightedClass)
  }

  deHighlightCommentId(commentId) {
    const jqCommentWrapper = this.getCommentWrapper(commentId)
    jqCommentWrapper.removeClass(this.options.highlightedClass)
  }

  initializeCommentActionsContent(jqButton, jqTip) {
    const jqCommentWrapper =
      jqButton.parents(this.options.selectors.commentWrapper)
    const commentId = jqCommentWrapper.data('commentId')
    const topicSlug = jqCommentWrapper.data('topicSlug')
    const hasPreviousComment =
      !!jqCommentWrapper.has(this.options.selectors.previousLinks).length
    const hasReplies =
      !!jqCommentWrapper.has(this.options.selectors.replyLinks).length
    const jqTemplate = this.jqTemplates.commentActions.clone()
    // Buttons are topmost in jqTemplate, hence .filter and not .find
    const jqButtonExpandCommentsDown =
      jqTemplate.filter(this.options.selectors.action.expandCommentsDown)
    jqButtonExpandCommentsDown.prop('hidden', !hasPreviousComment)
    const jqButtonExpandCommentsUp =
      jqTemplate.filter(this.options.selectors.action.expandCommentsUp)
    jqButtonExpandCommentsUp.prop('hidden', !hasReplies)
    const jqButtonExpandCommentsUpRecursive =
      jqTemplate.filter(this.options.selectors.action.expandCommentsUpRecursive)
    jqButtonExpandCommentsUpRecursive.prop('hidden', !hasReplies)
    if (hasReplies) {
      const constructedPathUpRecursive = this.urls.expandCommentsUpRecursive({
        commentId, topicSlug, scrollToId: commentId,
      })
      const constructedPathUp = this.urls.expandCommentsUp({
        commentId, topicSlug, scrollToId: commentId,
      })
      jqButtonExpandCommentsUpRecursive
        .prop('href', constructedPathUpRecursive)
      jqButtonExpandCommentsUp.prop('href', constructedPathUp)
    }
    if (hasPreviousComment) {
      const constructedPathDown = this.urls.expandCommentsDown({
        commentId, topicSlug, scrollToId: commentId,
      })
      jqButtonExpandCommentsDown.prop('href', constructedPathDown)
    }
    jqTip.find('.popover-content').empty().append(jqTemplate)
    jqTip.find('[data-toggle="tooltip"]').tooltip()
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.prepareUrlFormatStrings()
    this.jqTemplates = {
      commentActions: $(extractTemplateHtml(
        this.jqRoot.find(this.options.selectors.template.action)[0],
      )),
    }
    this.jqWrappers = {
      comments: this.jqRoot.find(this.options.selectors.commentWrapper),
    }
    this.jqWrappers.comments.find(this.options.selectors.previousLinks)
      .click(::this.onClickLinkPreviousComment)
      .hover(
        ::this.onMouseEnterLinkPreviousComment,
        ::this.onMouseLeaveLinkPreviousComment,
      )
    this.jqWrappers.comments.find(this.options.selectors.replyLinks)
      .click(::this.onClickLinkReplyComment)
      .hover(
        ::this.onMouseEnterLinkReplyComment,
        ::this.onMouseLeaveLinkReplyComment,
      )
    this.jqWrappers.comments.find(this.options.selectors.selfLinks)
      .click(::this.onClickLinkComment)
    const jqButtonCommentActions =
      this.jqWrappers.comments.find(this.options.selectors.commentActions)
    for (const button of jqButtonCommentActions) {
      popoverHovercontentAdd(button, {
        clickTakeOver: true,
        callbacks: {
          contentInit: ::this.initializeCommentActionsContent,
        },
      })
    }
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    usernameAdd(jqUsers)
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizerAdd(jqTimeElements)
    $(window).on('popstate', ::this.onPopState)
    this.scrollFix = new ScrollFix({
      callbacks: {
        getScrollToElement: ::this.getCommentWrapper,
        afterScrollTo: ::this.afterScrollTo,
        updateUrl: ::this.updateUrl,
      },
      scrollToInitial: this.options.scrollToId,
    })
    this.scrollFix.initialize()
    if (this.options.listingMode === 'commentListing') {
      this.paginator = paginatorInit({
        currentPageNo: 1,
        jqRoot: this.jqRoot.find(this.options.selectors.paginator),
        callbackLoadPage: ::this.onClickLoadPage,
      })
    }
  }
}

export function init(options) {
  $.when($.ready).then(() => {
    const commentListing = new CommentListing(options)
    commentListing.initialize()
  })
}
