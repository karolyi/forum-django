import $ from 'jquery'

class Paginator {
  onClickPaginateNumber(event) {
    event.preventDefault()
    const jqElement = $(event.currentTarget)
    const jqParentElement = jqElement.parent()
    if (jqParentElement.hasClass('active')) return
    jqElement.html($('<span/>', {
      class: 'fa fa-spinner fa-pulse fa-fw',
      'aria-hidden': true,
    }))
    this.clickedPageNo = parseInt(jqParentElement.data('pageId'), 10)
    this.options.jqRoot.find('.page-numbered a').each((idx, node) => {
      const jqNode = $(node)
      if (jqNode.is(jqElement)) return
      jqNode.replaceWith($('<span/>', {
        class: 'page-link',
        text: jqNode.text(),
      }))
    })
    this.options.callbackLoadPage(this.clickedPageNo)
  }

  constructor(options) {
    this.options = options
    this.options.jqRoot.find('.page-numbered a')
      .click(::this.onClickPaginateNumber)
  }
}

export function init(options) {
  return new Paginator(options)
}
