/* globals gettext, CKEDITOR */
// import $ from 'jquery'
import 'bootstrap/js/src/tooltip'
// import * as URI from 'urijs'
import { Pen } from 'pen'
import * as MYCSS from 'pen/src/pen.css'
// import * as common from './common'


// const cachedResponses = {
//   'www.stuff.com': '<b>wwwstuffreplacedtext</b>',
// }
console.debug('MYCSS', MYCSS)

// const sanitizeHtml = require('sanitize-html')

// const paginator = require('./paginator')
// const userName = require('./userName')
// const timeActualizer = require('./timeActualizer')
// const popOverHoverContent = require('./popOverHoverContent')

export class Instance {
  constructor(options) {
    this.options = options
  }

  initialize() {
    //   this.options.jqElement.trumbowyg({
    //     lang: common.options.languageInfo.code,
    //     removeformatPasted: true,
    //   })
    //   this.jqEditorElement = this.options.jqElement.data('trumbowyg').$ed
    //   this.jqEditorElement.on(
    //     'input', ::this.onInput).on('paste', ::this.onPaste)
    // this.simplemde = new SimpleMDE({ element: this.options.jqElement[0] })
    // console.debug('pen', this.options.jqElement[0], Pen)
    // $('body').append($('<script/>', {
    //   // rel: 'stylesheet',
    //   type: 'text/javascript',
    //   src: MYCSS.default,
    // }))
    const x = new Pen({
      editor: this.options.jqElement[0],
    })
    console.log(x)
  }
}

export function init(options) {
  const richMdTextArea = new Instance(options)
  richMdTextArea.initialize()
  return richMdTextArea
}
