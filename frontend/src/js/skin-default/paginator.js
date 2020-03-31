// const $ = require('jquery')

class Paginator {
  updateUi() {
    this.options.jqRoot.find('.page-numbered.active').removeClass('active')
    this.options.jqRoot
      .find(`.page-numbered[data-page-id=${this.currentPageNr}]`)
      .addClass('active')
  }

  onClickPaginateNumber(event) {
    event.preventDefault()
    const { parentElement } = event.currentTarget
    if (parentElement.classList.contains('active')) return
    this.currentPageNr = parseInt(parentElement.dataset.pageId, 10)
    if (this.currentPageNr > this.options.pageMax || this.currentPageNr < 1) {
      // Page number is out of bounds, reset it to 1
      this.currentPageNr = 1
    }
    this.options.callbackLoadPage(this.currentPageNr)
  }

  initVariables() {
    this.currentPageNr = this.options.currentPageNr
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
