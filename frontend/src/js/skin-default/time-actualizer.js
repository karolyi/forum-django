/* global Forum */
import 'bootstrap/js/src/tooltip'
import $ from 'jquery'
import moment from 'moment'
// const momentTimezone = require('moment-timezone')
import { observeRemoveJq } from './mutation-observer'

const {
  npgettext, interpolate, pgettext, gettext,
} = Forum.django
const instanceMap = new Map()
const options = {}
const formatStrOnePart = pgettext('naturaltime_js', '%(partOne)s ago')
const formatStrTwoParts =
  pgettext('naturaltime_js', '%(partOne)s, %(partTwo)s ago')

const calculateNatural = (currentMomentUtc, dateMomentUtc) => {
  const duration = moment.duration(currentMomentUtc.diff(dateMomentUtc))
  const secondsElapsed = duration.asSeconds()
  if (secondsElapsed === 0) {
    return gettext('now')
  }
  let partOne
  // Years
  const yearsCount = duration.years()
  const monthsCount = duration.months()
  if (yearsCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s year', '%s years', yearsCount)
    partOne = interpolate(fmt, [yearsCount])
    if (monthsCount === 0) {
      // No months applicable, return this
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Months
  const weeksCount = duration.weeks()
  if (monthsCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s month', '%s months', monthsCount)
    const interpolatedStr = interpolate(fmt, [monthsCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    if (weeksCount === 0) {
      // No weeks applicable, return this
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Weeks, days have to be subtracted with the week count
  const daysCount = duration.days() - (weeksCount * 7)
  if (weeksCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s week', '%s weeks', weeksCount)
    const interpolatedStr = interpolate(fmt, [weeksCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    if (daysCount === 0) {
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Days
  const hoursCount = duration.hours()
  if (daysCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s day', '%s days', daysCount)
    const interpolatedStr = interpolate(fmt, [daysCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    if (hoursCount === 0) {
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Hours
  const minutesCount = duration.minutes()
  if (hoursCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s hour', '%s hours', hoursCount)
    const interpolatedStr = interpolate(fmt, [hoursCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    if (minutesCount === 0) {
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Minutes
  const secondsCount = duration.seconds()
  if (minutesCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s minute', '%s minutes', minutesCount)
    const interpolatedStr = interpolate(fmt, [minutesCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    if (secondsCount === 0) {
      return interpolate(formatStrOnePart, { partOne }, true)
    }
  }
  // Seconds
  if (secondsCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s second', '%s seconds', secondsCount)
    const interpolatedStr = interpolate(fmt, [secondsCount])
    if (partOne) {
      return interpolate(
        formatStrTwoParts, { partOne, partTwo: interpolatedStr }, true,
      )
    }
    partOne = interpolatedStr
    return interpolate(formatStrOnePart, { partOne }, true)
  }

  // This shouldn't be reached normally
  return ''
}

const updateInstances = () => {
  const currentMomentUtc = moment.utc()
  for (const data of instanceMap.values()) {
    const naturalValue =
      calculateNatural(currentMomentUtc, data.momentInstance)
    data.jqElement.attr('data-original-title', naturalValue)
  }
}

setInterval(updateInstances, 60000)

const onRemoveElement = (domNode) => {
  instanceMap.delete(domNode)
}

export function add(jqTimeElements) {
  const currentMomentUtc = moment.utc()
  for (const domNode of jqTimeElements) {
    const jqElement = $(domNode)
    const momentInstance = moment.utc(jqElement.attr('datetime'))
    if (!instanceMap.has(domNode)) {
      instanceMap.set(domNode, { jqElement, momentInstance })
      jqElement.tooltip()
      jqElement.attr(
        'data-original-title',
        calculateNatural(currentMomentUtc, momentInstance),
      )
    }
  }
  observeRemoveJq(jqTimeElements, onRemoveElement)
}

export function init(optionsPassed) {
  for (const [key, value] of optionsPassed) {
    options[key] = optionsPassed[value]
  }
}
