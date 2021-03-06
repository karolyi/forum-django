import $ from 'jquery'
import 'select2'
import templateSettings from 'lodash/templateSettings'
// The navbar needs these on all pages
import 'bootstrap/js/src/dropdown'
import 'bootstrap/js/src/collapse'
import { Settings as LuxonSettings } from 'luxon'
import { init as timeActualizerInit } from './time-actualizer'

window.$ = $

const select2Hu = require('select2/src/js/select2/i18n/hu')
const select2De = require('select2/src/js/select2/i18n/de')

// Python formatstring will work this way
templateSettings.interpolate = /{([\s\S]+?)}/g

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
  LuxonSettings.defaultLocale = optionsPassed.languageInfo.code
  timeActualizerInit({
    languageInfo: optionsPassed.languageInfo,
  })
}

export function extractTemplateHtml(domTemplateElement) {
  const tempElement = document.createElement('p')
  const templateCopy = document.importNode(domTemplateElement, true)
  const templateCopyArray = Array.prototype.slice.call(
    templateCopy.content.childNodes,
  )
  for (const item of templateCopyArray) tempElement.appendChild(item)
  return tempElement.innerHTML
}

/**
 * Cookie getter function from here:
 * https://docs.djangoproject.com/en/dev/ref/csrf/
 * @param  {string} name The cookie name
 * @return {string}      Cookie value
 */
export function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const cookieTrimmed = $.trim(cookie)
      // Does this cookie string begin with the name we want?
      if (cookieTrimmed.substring(0, name.length + 1) === `${name}=`) {
        cookieValue =
          decodeURIComponent(cookieTrimmed.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function addCsrfHeader(xhr) {
  xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'))
}

/**
 * Update a hidden CSRF token in a form, using the cookie value
 * @param {Object} jqElement The element to set the cookie value to
 * @return {string}          The CSRF cookie value
 */
export function updateCsrfToken(jqElement) {
  const csrfToken = getCookie('csrftoken')
  if (jqElement) {
    jqElement.val(csrfToken)
  }
  return csrfToken
}

export function escapeHtml(text) {
  return $('<div/>', {
    text,
  }).html()
}

const calcNavbarHeight = () => {
  // Calculate navbar height
  const cssNavbarHeight = $(options.selectors.navbar).css('height')
  options.navbarHeight = Math.ceil(parseFloat(cssNavbarHeight.split('px')[0]))
}

$.when($.ready).then(() => {
  calcNavbarHeight()
})
