const $ = require('jquery')
require('select2')
const select2Hu = require('select2/src/js/select2/i18n/hu')
const select2De = require('select2/src/js/select2/i18n/de')

// English language is self-contained in select2, others not.
$.fn.select2.amd.define('select2/i18n/hu', select2Hu)
$.fn.select2.amd.define('select2/i18n/de', select2De)

export const options = {
  /* eslint-disable new-cap */
  promiseWindowLoad: $.Deferred(),
  /* eslint-enable new-cap */
}

$(window).on('load', () => {
  options.promiseWindowLoad.resolve()
})

export function init(optionsPassed) {
  for (const key of Object.keys(optionsPassed)) {
    options[key] = optionsPassed[key]
  }
}

export function extractTemplateHtml(domTemplateElement) {
  const tempElement = document.createElement('p')
  const templateCopy = document.importNode(domTemplateElement, true)
  const templateCopyArray = Array.prototype.slice.call(
    templateCopy.content.childNodes)
  for (const item of templateCopyArray) tempElement.appendChild(item)
  return tempElement.innerHTML
}

const calcNavbarHeight = () => {
  // Calculate navbar height
  const cssNavbarHeight = $(options.selectors.navbar).css('height')
  options.navbarHeight = Math.ceil(parseFloat(cssNavbarHeight.split('px')[0]))
}

$.when($.ready).then(() => {
  calcNavbarHeight()
})
