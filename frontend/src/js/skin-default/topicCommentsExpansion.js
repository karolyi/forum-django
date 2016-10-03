/* global interpolate */
import { CommentListing } from './topicCommentListing'

const $ = require('jquery')

class CommentsExpansion extends CommentListing {

  /**
   * The difference here is, the comment ID in the URL always stays
   * the original passed one, and only the scrollToId part of the URL
   * changes.
   */
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
      this.options.topicSlugOriginal, this.options.commentId, commentIdLinked)
    history.pushState({}, null, constructedPath)
    this.scrollFix.scrollTo(commentIdLinked)
  }

  constructPathFromWrapper(jqCommentWrapper) {
    const commentId = jqCommentWrapper.data('commentId')
    return this.constructPathFromData(
      this.options.topicSlugOriginal, this.options.commentId, commentId)
  }

}

export function init(options) {
  $.when($.ready).then(() => {
    const commentsExpansion = new CommentsExpansion(options)
    commentsExpansion.initialize()
  })
}
