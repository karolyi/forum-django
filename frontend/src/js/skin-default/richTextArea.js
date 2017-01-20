/* globals gettext */
require('bootstrap/js/src/tooltip')
const $ = require('jquery')
const common = require('./common')
const URI = require('urijs')

const cachedResponses = {
  'www.stuff.com': '<b>wwwstuffreplacedtext</b>',
}

/**
 * <turbowyg>
 */
require('trumbowyg')
// Languages of choice
require('trumbowyg/dist/langs/hu.min')
require('trumbowyg/dist/langs/de.min')
// Modules
require('trumbowyg/plugins/cleanpaste/trumbowyg.cleanpaste')
// Load SVG icons
$.trumbowyg.svgPath = require('trumbowyg/dist/ui/icons.svg')
/**
 * </turbowyg>
 */

const sanitizeHtml = require('sanitize-html')

// const paginator = require('./paginator')
// const userName = require('./userName')
// const timeActualizer = require('./timeActualizer')
// const popOverHoverContent = require('./popOverHoverContent')

export class Instance {
  constructor(options) {
    this.options = options
  }

  onXhrNoEmbedSuccess(data, type, jqXhr) {
    this.options.jqElement.trumbowyg('saveRange')
    cachedResponses[jqXhr.requestedUrl] = data.html
    const oldContent = this.options.jqElement.trumbowyg('html')
    const newContent = oldContent.replace(jqXhr.requestedUrl, data.html)
    if (newContent !== oldContent) {
      this.options.jqElement.trumbowyg('html', newContent)
    }
    this.options.jqElement.trumbowyg('restoreRange')
  }

  // onXhrNoEmbedError(data, type, jqXhr) {}

  urlIterator(url) {
    if (cachedResponses[url] === false) return
    if (cachedResponses[url]) {
      this.currentContent =
        this.currentContent.replace(url, cachedResponses[url])
      return
    }
    const parsedUrl = URI(url)
    if (parsedUrl.host().indexOf('.') === -1) return
    $.when($.ajax({
      url: common.options.urls.noEmbed,
      /* eslint-disable no-param-reassign */
      beforeSend: (jqXhr) => { jqXhr.requestedUrl = url },
      /* eslint-enable no-param-reassign */
      data: { url },
      dataType: 'json',
    })).then(::this.onXhrNoEmbedSuccess, ::this.onXhrNoEmbedError)
  }

  convertVisibleUrls() {
    this.currentContent = this.options.jqElement.trumbowyg('html')
    const oldContent = this.options.jqElement.trumbowyg('html')
    URI.withinString(this.jqEditorElement[0].innerText, ::this.urlIterator)
    if (oldContent !== this.currentContent) {
      this.options.jqElement.trumbowyg('html', this.currentContent)
    }
  }

  cleanHtml() {
    this.options.jqElement.trumbowyg('saveRange')
    const oldContent = this.options.jqElement.trumbowyg('html')
    const newContent = sanitizeHtml(oldContent)
    if (newContent !== oldContent) {
      this.options.jqElement.trumbowyg('html', newContent)
    }
    this.options.jqElement.trumbowyg('restoreRange')
  }

  onPaste() {
    this.cleanHtml()
    // this.convertVisibleUrls()
  }

  onInput() {
    this.cleanHtml()
    // this.convertVisibleUrls()
  }

  // searchUsernames(params, success, failure) {
  //   const ajaxData = {
  //     name_contains: params.data.term,
  //     page: params.data.page || 1,
  //   }
  //   $.when($.ajax({
  //     url: this.options.urls.userSearch,
  //     data: ajaxData,
  //     dataType: 'json',
  //   })).then(success, failure)
  // }

  initialize() {
    this.options.jqElement.trumbowyg({
      lang: common.options.languageInfo.code,
      removeformatPasted: true,
    })
    this.jqEditorElement = this.options.jqElement.data('trumbowyg').$ed
    this.jqEditorElement.on(
      'input', ::this.onInput).on('paste', ::this.onPaste)
  }
}

export function init(options) {
  const richMdTextArea = new Instance(options)
  richMdTextArea.initialize()
  return richMdTextArea
}
