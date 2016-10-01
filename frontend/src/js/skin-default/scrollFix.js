const $ = require('jquery')
const common = require('./common')

/**
 * This is a generic utility to set the page to a specific scroll
 * position on load, specified by the initializing module.
 *
 * Also, use passed callbacks for executing functions when the window
 * is scrolled (generally, set an URL with pushState when scrolled).
 */
export class ScrollFix {
  constructor(options) {
    this.isPageScrolled = false
    this.isScrollingOnPurpose = false
    this.intervalInitialScroll = null
    this.options = options
  }

  onScroll() {
    if (!this.isScrollingOnPurpose) {
      this.isPageScrolled = true
      this.clearInitialScrollInterval()
    }
    if (!this.options.callbacks.updateUrl) return
    if (this.timeoutUpdateUrl) clearTimeout(this.timeoutUpdateUrl)
    this.timeoutUpdateUrl = setTimeout(this.options.callbacks.updateUrl, 1000)
  }

  onCompleteScrollAnimation(jqNewScrollToElement, isScrolled) {
    this.isScrollingOnPurpose = false
    if (!this.options.callbacks.afterScrollTo) return
    this.options.callbacks.afterScrollTo(jqNewScrollToElement, isScrolled)
  }

  scrollTo(parameterScrollTo) {
    // Return if we don't have a position telling callback function
    if (!this.options.callbacks.getScrollToElement) return
    const jqNewScrollToElement =
      this.options.callbacks.getScrollToElement(parameterScrollTo)
    const newScrollTop = jqNewScrollToElement.offset().top
    const jqDocument = $(document)
    const actualScrollTop = newScrollTop - common.options.navbarHeight
    const isScrolled = jqDocument.scrollTop() !== actualScrollTop
    setTimeout(() => {
      // Execute the finish animation even when we don't scroll
      this.onCompleteScrollAnimation(jqNewScrollToElement, isScrolled)
    }, 10)
    // Scroll to it only when necessary
    if (!isScrolled) return
    this.isScrollingOnPurpose = true
    jqDocument.scrollTop(actualScrollTop)
    // Browsers keep scrolling after scrollTop has been issued, hence
    // the setTimeout
  }

  clearInitialScrollInterval() {
    if (this.intervalInitialScroll) {
      clearInterval(this.intervalInitialScroll)
      this.intervalInitialScroll = null
    }
  }

  onLoadWindow() {
    if (this.isPageScrolled) return
    if (this.options.scrollToInitial) {
      this.scrollTo(this.options.scrollToInitial)
    }
    this.clearInitialScrollInterval()
  }

  initialize() {
    $(window).scroll(::this.onScroll)
    $.when(common.options.promiseWindowLoad).then(::this.onLoadWindow)
    if (this.options.scrollToInitial) {
      this.scrollTo(this.options.scrollToInitial)
      // Start the scroll interval
      this.intervalInitialScroll = setInterval(() => {
        this.scrollTo(this.options.scrollToInitial)
      }, 1000)
    }
  }
}
