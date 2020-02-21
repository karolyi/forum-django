/* globals gettext, interpolate */
import $ from 'jquery'
import 'bootstrap/js/src/tooltip'
import 'bootstrap/js/src/tab'
import URI from 'urijs'
import TextareaEditor, { formats as editorFormats } from 'textarea-editor'
import template from './template/rich-text-area.html'
import {
  options as commonOptions, addCsrfHeader, updateCsrfToken, escapeHtml,
} from './common'

editorFormats.strikethrough = {
  prefix: '~~',
  suffix: '~~',
}
editorFormats.forumEmbed = {
  block: true,
  prefix: '[EMBED:',
  suffix: ']',
}

const unknownError = gettext('Unknown error')
const errorStr = gettext(
  'An error occurred. If the error persists, please notify the ' +
  'administrators. The error was: <br><b>%(errorText)s</b>',
)
const loadingText = gettext('Loading ...')
const anyCharRegex = /^\S+$/i

// const cachedResponses = {
//   'www.stuff.com': '<b>wwwstuffreplacedtext</b>',
// }

// const paginator = require('./paginator')
// const userName = require('./userName')
// const timeActualizer = require('./timeActualizer')
// const popOverHoverContent = require('./popOverHoverContent')

export class Instance {
  constructor(options) {
    this.options = options
  }

  onClickTab(event) {
    const jqElement = $(event.target)
    event.preventDefault()
    jqElement.tab('show')
    if (!jqElement.is('.tab-preview')) return
    // Preview is clicked, update content
    this.updatePreview()
  }

  onPaste() {
    this.isPasteHappened = true
    this.updateSelections()
  }

  onInput() {
    if (this.isPasteHappened) {
      this.isPasteHappened = false
      this.evaluateUrls()
      // return
    }
    // console.debug('onInput', this.options.jqElement.val())
  }

  onClickToolbarBold() {
    this.editor.toggle('bold')
  }

  onClickToolbarItalic() {
    this.editor.toggle('italic')
  }

  onClickToolbarStrikethrough() {
    this.editor.toggle('strikethrough')
  }

  onClickToolbarUl() {
    this.editor.toggle('unorderedList')
  }

  onClickToolbarOl() {
    this.editor.toggle('unorderedList')
  }

  onClickToolbarQuote() {
    this.editor.toggle('blockquote')
  }

  onClickToolbarH1() {
    this.editor.toggle('header1')
    // this.editor.toggle('header1')
  }

  onClickToolbarH2() {
    this.editor.toggle('header2')
  }

  onClickToolbarH3() {
    this.editor.toggle('header3')
  }

  onClickToolbarEmbed() {
    // this.insertFormattingBeforeAfter('[EMBED:', ']', true)
    this.editor.toggle('forumEmbed')
  }

  updateSelections() {
    this.selectionStart = this.options.jqElement.prop('selectionStart')
    this.selectionEnd = this.options.jqElement.prop('selectionEnd')
  }

  onXhrSuccessUpdatePreview(data) {
    this.jqPreviewWrapper.html(data.html)
    updateCsrfToken(this.jqCsrfToken)
  }

  onXhrErrorUpdatePreview(data) {
    let errorText = unknownError
    if (data.responseJSON && data.responseJSON.message) {
      errorText = data.responseJSON.message
    }
    const errorStrFormatted =
      interpolate(errorStr, { errorText: escapeHtml(errorText) }, true)
    this.jqPreviewWrapper.html(
      '<span class="text-danger">' +
      '<i class="fa fa-exclamation-triangle"></i> ' +
      `${errorStrFormatted}</span>`,
    )
    updateCsrfToken(this.jqCsrfToken)
  }

  evaluateUrls() {
    // const oldSelectionStart = this.selectionStart
    // const oldSelectionEnd = this.selectionEnd
    this.updateSelections()
    const text = this.options.jqElement.val()
    URI.withinString(text, (urlFound) => {
      console.log('found url:', urlFound)
    })
  }

  insertFormattingBeforeAfter(prefix, suffix, newBlock = false) {
    this.options.jqElement.focus()
    const text = this.options.jqElement.val()
    const selectionStart = this.options.jqElement.prop('selectionStart')
    const selectionEnd = this.options.jqElement.prop('selectionEnd')
    const selectionBefore = text.slice(0, selectionStart)
    const selection = text.slice(selectionStart, selectionEnd)
    if (selection.indexOf('\n') !== -1) {
      // Don't add formatting when multiple lines detected
      return
    }
    const selectionAfter = text.slice(selectionEnd, text.length)
    let formatPrefix = prefix
    let formatSuffix = suffix
    let newLines
    if (newBlock) {
      // This element has to be put into a new paragraph
      const twoCharsBefore = text.slice(selectionStart - 2, selectionStart)
      const twoCharsAfter = text.slice(selectionEnd, selectionEnd + 2)
      if (anyCharRegex.test(twoCharsBefore)) {
        // Add new lines before the element
        newLines = twoCharsBefore[1] === '\n' ? '\n' : '\n\n'
        formatPrefix = `${newLines}${prefix}`
      }
      if (anyCharRegex.test(twoCharsAfter)) {
        // Add new lines after the element
        newLines = twoCharsAfter[0] === '\n' ? '\n' : '\n\n'
        formatSuffix = `${suffix}${newLines}`
      }
    }
    const newValue =
      `${selectionBefore}${formatPrefix}${selection}` +
      `${formatSuffix}${selectionAfter}`
    this.options.jqElement.val(newValue)
    this.options.jqElement
      .prop('selectionStart', selectionStart + formatPrefix.length)
      .prop('selectionEnd', selectionEnd + formatPrefix.length)
      .focus()
  }

  updatePreview() {
    const fieldValue = this.options.jqElement.val()
    this.jqPreviewWrapper.html(
      '<i class="fa fa-spinner fa-pulse fa-fw"></i>' +
      `<span class="sr-only">${loadingText}</span>`,
    )
    $.when($.ajax({
      url: commonOptions.urls.mdParser,
      beforeSend: addCsrfHeader,
      dataType: 'json',
      method: 'POST',
      data: {
        text_md: fieldValue,
      },
    })).then(::this.onXhrSuccessUpdatePreview, ::this.onXhrErrorUpdatePreview)
    // this.jqPreviewWrapper.html(htmlContent)
  }

  initBtnToolbar() {
    const jqToolbar = this.jqTemplate.find('.btn-toolbar')
    jqToolbar.find('.toolbar-bold')
      .prop('title', gettext('Insert bold formatting'))
      .click(::this.onClickToolbarBold)
    jqToolbar.find('.toolbar-italic')
      .prop('title', gettext('Insert italic formatting'))
      .click(::this.onClickToolbarItalic)
    jqToolbar.find('.toolbar-strikethrough')
      .prop('title', gettext('Insert strikethrough formatting'))
      .click(::this.onClickToolbarStrikethrough)
    jqToolbar.find('.toolbar-ul')
      .prop('title', gettext('Insert unordered list formatting'))
      .click(::this.onClickToolbarUl)
    jqToolbar.find('.toolbar-ol')
      .prop('title', gettext('Insert ordered list formatting'))
      .click(::this.onClickToolbarOl)
    jqToolbar.find('.toolbar-quote')
      .prop('title', gettext('Insert quote formatting'))
      .click(::this.onClickToolbarQuote)
    jqToolbar.find('.toolbar-h1')
      .prop('title', gettext('Insert heading 1 formatting'))
      .click(::this.onClickToolbarH1)
    jqToolbar.find('.toolbar-h2')
      .prop('title', gettext('Insert heading 2 formatting'))
      .click(::this.onClickToolbarH2)
    jqToolbar.find('.toolbar-h3')
      .prop('title', gettext('Insert heading 3 formatting'))
      .click(::this.onClickToolbarH3)
    jqToolbar.find('.toolbar-embed')
      .prop('title', gettext('Embed video/link/image'))
      .click(::this.onClickToolbarEmbed)
    jqToolbar.find('[data-toggle=tooltip]').tooltip()
  }

  initialize() {
    this.jqTemplate = $(template)
    this.jqPreviewWrapper = this.jqTemplate.find('.tabpane-preview')
    this.id = this.options.jqElement.attr('id')
    // Setup tabs
    this.jqTemplate.find('.tab-edit')
      .prop('href', `#tabpane_edit_${this.id}`)
      .attr('aria-controls', `tabpane_edit_${this.id}`)
      .text(gettext('Edit'))
    this.jqTemplate.find('.tab-preview')
      .prop('href', `#tabpane_preview_${this.id}`)
      .attr('aria-controls', `tabpane_preview_${this.id}`)
      .text(gettext('Preview'))
    // Setup tabpanes
    this.jqTemplate.find('.tabpane-edit')
      .prop('id', `tabpane_edit_${this.id}`)
    this.jqTemplate.find('.tabpane-edit .textarea-wrapper')
      .append(this.options.jqElement)
    this.jqTemplate.find('.tabpane-preview')
      .prop('id', `tabpane_preview_${this.id}`)
    this.jqTemplate.find('a').click(::this.onClickTab)
    this.options.jqElement
      .on('paste', ::this.onPaste)
      .on('input', ::this.onInput)
    this.editor = new TextareaEditor(this.options.jqElement[0])
    this.initBtnToolbar()
    this.options.jqWrapper.append(this.jqTemplate)
    this.jqCsrfToken =
      this.options.jqElement
        .parents('form')
        .find('input[name=csrfmiddlewaretoken]')
  }
}

export function init(options) {
  const richMdTextArea = new Instance(options)
  richMdTextArea.initialize()
  return richMdTextArea
}
