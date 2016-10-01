require('bootstrap/js/src/popover')
const $ = require('jquery')
const mutationObserver = require('./mutationObserver')

const elementsMap = new Map()

/**
 * This module expands the bootstrap provided popover with showing the
 * popover until it's content is hovered or until the original element
 * is hovered.
 *
 * We have element and tip. The element is the element initialized with
 * popover, and the tip is the popver tip element itself.
 */

const initializeTipContent = (jqElement, jqTip) => {
  if (jqTip.data('isInitialized')) return
  const options = elementsMap.get(jqElement[0])
  jqTip.data('isInitialized', true)
  if (!options.callbacks.contentInit) return
  jqElement.on('inserted.bs.popover', () => {
    options.callbacks.contentInit(jqElement, jqTip)
  })
}

const onMouseLeaveTip = (jqElement, jqTip) => {
  jqTip.data('isTipMouseEntered', false)
  setTimeout(() => {
    if (jqElement.data('isButtonMouseEntered')) return
    jqElement.popover('hide')
    jqTip.data('isShown', false)
  })
}

const onMouseEnterTip = (jqElement, jqTip) => {
  jqTip.data('isTipMouseEntered', true)
}

const onMouseLeaveElement = (event) => {
  const jqElement = $(event.currentTarget)
  jqElement.data('isButtonMouseEntered', false)
  setTimeout(() => {
    const popOverInstance = jqElement.data('bs.popover')
    const jqTip = $(popOverInstance.getTipElement())
    if (jqTip.data('isTipMouseEntered')) return
    jqElement.popover('hide')
    jqTip.data('isShown', false)
  })
}

const bindEventsToTip = (jqElement, jqTip) => {
  // Don't bind mouseleave/mouseenter events more than once
  if (jqTip.data('isAlreadyBound')) return
  jqTip.mouseleave(() => {
    onMouseLeaveTip(jqElement, jqTip)
  }).mouseenter(() => {
    onMouseEnterTip(jqElement, jqTip)
  })
  jqTip.data('isAlreadyBound', true)
}

const onMouseEnterElement = (event) => {
  const jqElement = $(event.currentTarget)
  jqElement.data('isButtonMouseEntered', true)
  const popOverInstance = jqElement.data('bs.popover')
  const jqTip = $(popOverInstance.getTipElement())
  if (!jqTip.data('isShown')) {
    initializeTipContent(jqElement, jqTip)
    jqTip.data('isShown', true)
    jqElement.popover('show')
  }
  bindEventsToTip(jqElement, jqTip)
}

const onClickElement = (event) => {
  event.preventDefault()
  const jqElement = $(event.currentTarget)
  const popOverInstance = jqElement.data('bs.popover')
  const jqTip = $(popOverInstance.getTipElement())
  if (!jqTip.data('isShown')) {
    initializeTipContent(jqElement, jqTip)
    jqElement.popover('show')
    jqTip.data('isShown', true)
  } else {
    jqElement.popover('hide')
    jqTip.data('isShown', false)
  }
  bindEventsToTip(jqElement, jqTip)
}

export function remove(element) {
  elementsMap.delete(element)
}

export function add(element, options) {
  elementsMap.set(element, options)
  mutationObserver.observeRemoveNode(element, remove)
  const jqElement = $(element)
  const optionsPopOver = options.popover || {}
  optionsPopOver.trigger = 'manual'
  jqElement
    // an empty 'data-content' has to be added, otherwise popover won't
    // initialize
    .attr('data-content', ' ')
    .mouseenter(onMouseEnterElement)
    .mouseleave(onMouseLeaveElement)
    .popover(optionsPopOver)
  if (options.clickTakeOver) {
    // Assign the click action too
    jqElement.click(onClickElement)
  }
}
