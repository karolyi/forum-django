import $ from 'jquery'
import 'bootstrap/js/src/popover'
import { observeRemoveJq } from './mutation-observer'
/**
 * This module expands the bootstrap provided popover with showing the
 * popover until it's content is hovered or until the original element
 * is hovered.
 *
 * We have element and tip. The element is the element initialized with
 * popover, and the tip is the popover tip element itself.
 */
const tooltipGroups = {}

const initializeTipContent = (jqElement, jqTip) => {
  if (jqTip.data('isInitialized')) return
  const options = jqElement.data('optionsPopoverHovercontent')
  jqTip.data('isInitialized', true)
  if (!options.callbacks.contentInit) return
  jqElement.on('inserted.bs.popover', () => {
    options.callbacks.contentInit(jqElement, jqTip)
  })
}

const onMouseLeaveTip = (jqElement, jqTip) => {
  jqTip.data('isTipMouseEntered', false)
  setTimeout(() => {
    if (jqElement.data('isElementMouseEntered')) return
    jqElement.popover('hide')
    jqTip.data('isShown', false)
  })
}

const onMouseEnterTip = (jqElement, jqTip) => {
  jqElement.data('isElementMouseEntered', false)
  jqTip.data('isTipMouseEntered', true)
}

const hideTip = (jqElement, force) => {
  jqElement.data('isElementMouseEntered', false)
  const popOverInstance = jqElement.data('bs.popover')
  const jqTip = $(popOverInstance.getTipElement())
  if (jqTip.data('isTipMouseEntered') && !force) return
  jqElement.popover('hide')
  jqTip.data('isShown', false)
}

const onMouseLeaveElement = (event) => {
  const jqElement = $(event.currentTarget)
  setTimeout(() => {
    hideTip(jqElement, false)
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
  jqElement.data('isElementMouseEntered', true)
  jqElement.data('isTipMouseEntered', false)
  const options = jqElement.data('optionsPopoverHovercontent')
  if (options.groupName) {
    for (const jqItem of tooltipGroups[options.groupName]) {
      if (jqItem.is(jqElement)) continue
      hideTip(jqItem, true)
    }
  }
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
  // const jqElement = $(event.currentTarget)
  // const popOverInstance = jqElement.data('bs.popover')
  // const jqTip = $(popOverInstance.getTipElement())
  // if (!jqTip.data('isShown')) {
  //   initializeTipContent(jqElement, jqTip)
  //   jqElement.popover('show')
  //   jqTip.data('isShown', true)
  // } else {
  //   jqElement.popover('hide')
  //   jqTip.data('isShown', false)
  // }
  // bindEventsToTip(jqElement, jqTip)
}

const onRemoveObservedElement = (node) => {
  const jqElement = $(node)
  for (const setJqItems of Object.values(tooltipGroups)) {
    for (const jqItem of setJqItems) {
      if (jqElement.is(jqItem)) setJqItems.delete(jqItem)
    }
  }
}

export function add(targetNode, options) {
  const jqElement = $(targetNode)
  observeRemoveJq(jqElement, onRemoveObservedElement)
  // Hang all the options on the element, so it doesn't need to be
  // listened for garbage collection on DOM removal
  jqElement.data('optionsPopoverHovercontent', options)
  const optionsPopover = options.popover || {}
  optionsPopover.trigger = 'manual'
  jqElement
    // an empty 'data-content' has to be added, otherwise popover won't
    // initialize
    .attr('data-content', ' ')
    .mouseenter(onMouseEnterElement)
    .mouseleave(onMouseLeaveElement)
    .popover(optionsPopover)
  if (options.clickTakeOver) {
    // Assign the click action too
    jqElement.click(onClickElement)
  }
  if (options.groupName) {
    if (!tooltipGroups[options.groupName]) {
      tooltipGroups[options.groupName] = new Set()
    }
    tooltipGroups[options.groupName].add(jqElement)
  }
}

export function clearGroup(groupName) {
  for (const jqItem of tooltipGroups[groupName]) jqItem.popover('hide')
}
