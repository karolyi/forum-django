const $ = require('jquery')
const common = require('./common')
// const paginator = require('./paginator')
const userName = require('./userName')
const timeActualizer = require('./timeActualizer')

class CommentListing {
  constructor(options) {
    this.options = options
    this.isPageScrolled = false
    this.isScrollingOnPurpose = false
    this.intervalInitialScroll = null
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
  scrollCallback() {
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
      // This shouldn't be reached normally
      return
    }
    const topCommentId = jqTopComment.data('commentId')
    const constructedUrl = this.constructUrlPath(topCommentId)
    if (constructedUrl === location.pathname) return
    history.replaceState({}, null, constructedUrl)
  }

  onScroll() {
    if (!this.isScrollingOnPurpose) {
      this.isPageScrolled = true
      this.clearInitialScrollInterval()
    }
    if (this.scrollTimeout) clearTimeout(this.scrollTimeout)
    this.scrollTimeout = setTimeout(::this.scrollCallback, 1000)
  }

  onCompleteScrollAnimation() {
    this.isScrollingOnPurpose = false
  }

  scrollTo(commentId) {
    const jqCommentWrapper =
      this.jqWrappers.comments.filter(`[data-comment-id=${commentId}]`)
    const jqDocument = $(document)
    // Flash the linked comment
    jqCommentWrapper.addClass(this.options.highlightedClass)
    setTimeout(() => {
      jqCommentWrapper.removeClass(this.options.highlightedClass)
    }, 0)
    // Scroll to it only when necessary
    const newScrollTop =
      jqCommentWrapper.offset().top - common.options.navbarHeight
    if (jqDocument.scrollTop() === newScrollTop) return
    this.isScrollingOnPurpose = true
    jqDocument.scrollTop(
      jqCommentWrapper.offset().top - common.options.navbarHeight)
    // Browsers keep scrolling after scrollTop has been issued, hence
    // the setTimeout
    setTimeout(::this.onCompleteScrollAnimation, 10)
  }

  onClickCommentLink(event) {
    const previousCommentId = event.currentTarget.dataset.linkTo
    const jqExistingComment =
      this.jqWrappers.comments.filter(`[data-comment-id=${previousCommentId}]`)
    if (!jqExistingComment.length) {
      // The linked comment is not on this page
      return
    }
    event.preventDefault()
    history.pushState({}, null, event.currentTarget.href)
    this.scrollTo(previousCommentId)
  }

  onPopState() {
    const commentId = document.location.pathname.split('/')[3]
    if (!commentId) return
    this.scrollTo(commentId)
  }

  onLoadWindow() {
    if (this.isPageScrolled) return
    if (this.options.scrollTo) this.scrollTo(this.options.scrollTo)
    this.clearInitialScrollInterval()
  }

  clearInitialScrollInterval() {
    if (this.intervalInitialScroll) {
      clearInterval(this.intervalInitialScroll)
      this.intervalInitialScroll = null
    }
  }

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqTemplates = {

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
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
    $(window).scroll(::this.onScroll).on('popstate', ::this.onPopState)
    $.when(common.options.promiseWindowLoad).then(::this.onLoadWindow)
    if (this.options.scrollTo) {
      this.scrollTo(this.options.scrollTo)
      // Start the scroll interval
      this.intervalInitialScroll = setInterval(() => {
        this.scrollTo(this.options.scrollTo)
      }, 1000)
    }
  }
}


export function init(options) {
  $.when($.ready).then(() => {
    const commentListing = new CommentListing(options)
    commentListing.initialize()
  })
}
