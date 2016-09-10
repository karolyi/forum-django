const $ = require('jquery')
const common = require('./common')
const paginator = require('./paginator')
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
    if (constructedUrl === window.location.pathname) return
    history.pushState({}, null, constructedUrl)
  }

  onScroll() {
    if (this.scrollTimeout) clearTimeout(this.scrollTimeout)
    this.scrollTimeout = setTimeout(::this.scrollCallback, 1000)
  }

  scrollTo(commentId) {
    const jqCommentWrapper =
      this.jqWrappers.comments.filter(`[data-comment-id=${commentId}]`)
    $('html, body').animate({
      scrollTop: jqCommentWrapper.offset().top - common.options.navbarHeight,
    }, common.options.scrollSpeed)
  }

  onClickPreviousLink(event) {
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

  initialize() {
    this.jqRoot = $(this.options.selectors.root)
    this.jqTemplates = {

    }
    this.jqWrappers = {
      comments: this.jqRoot.find(this.options.selectors.commentWrapper),
    }
    this.jqWrappers.comments.find(this.options.selectors.previousLinks)
      .click(::this.onClickPreviousLink)
    const jqUsers = this.jqRoot.find('[data-toggle=username]')
    userName.add({
      jqUsers,
    })
    const jqTimeElements = this.jqRoot.find('.forum-time')
    timeActualizer.add(jqTimeElements)
    $(window).scroll(::this.onScroll)
    if (this.options.scrollTo) {
      this.scrollTo(this.options.scrollTo)
    }
  }
}


export function init(options) {
  $.when($.ready).then(() => {
    const commentListing = new CommentListing(options)
    commentListing.initialize()
  })
}
