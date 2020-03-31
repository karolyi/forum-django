// const $ = require('jquery')

class Paginator {
  updateUi() {
    this.options.jqRoot.find('.page-numbered.active').removeClass('active')
    this.options.jqRoot
      .find(`.page-numbered[data-page-id=${this.currentPageNo}]`)
      .addClass('active')
  }

  onClickPaginateNumber(event) {
    event.preventDefault()
    const { parentElement } = event.currentTarget
    if (parentElement.classList.contains('active')) return
    this.currentPageNo = parseInt(parentElement.dataset.pageId, 10)
    this.options.callbackLoadPage(this.currentPageNo)
  }

  initVariables() {
    this.currentPageNo = this.options.currentPageNo
    this.options.jqRoot.find('.page-numbered a')
      .click(::this.onClickPaginateNumber)
  }

  constructor(options) {
    this.options = options
    this.initVariables()
  }
}

export function init(options) {
  const paginator = new Paginator(options)
  return paginator
}
