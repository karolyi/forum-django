/* global npgettext, interpolate, pgettext, gettext */
require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
const $ = require('jquery')
const moment = require('moment')
// const momentTimezone = require('moment-timezone')
const mutationObserver = require('./mutationObserver')

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
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Months
  const weeksCount = duration.weeks()
  if (monthsCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s month', '%s months', monthsCount)
    const interpolatedStr = interpolate(fmt, [monthsCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    if (weeksCount === 0) {
      // No weeks applicable, return this
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Weeks, days have to be subtracted with the week count
  const daysCount = duration.days() - (weeksCount * 7)
  if (weeksCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s week', '%s weeks', weeksCount)
    const interpolatedStr = interpolate(fmt, [weeksCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    if (daysCount === 0) {
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Days
  const hoursCount = duration.hours()
  if (daysCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s day', '%s days', daysCount)
    const interpolatedStr = interpolate(fmt, [daysCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    if (hoursCount === 0) {
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Hours
  const minutesCount = duration.minutes()
  if (hoursCount > 0) {
    const fmt = npgettext('naturaltime_js', '%s hour', '%s hours', hoursCount)
    const interpolatedStr = interpolate(fmt, [hoursCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    if (minutesCount === 0) {
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Minutes
  const secondsCount = duration.seconds()
  if (minutesCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s minute', '%s minutes', minutesCount)
    const interpolatedStr = interpolate(fmt, [minutesCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    if (secondsCount === 0) {
      return interpolate(formatStrOnePart, {
        partOne,
      }, true)
    }
  }
  // Seconds
  if (secondsCount > 0) {
    const fmt =
      npgettext('naturaltime_js', '%s second', '%s seconds', secondsCount)
    const interpolatedStr = interpolate(fmt, [secondsCount])
    if (partOne) {
      return interpolate(formatStrTwoParts, {
        partOne,
        partTwo: interpolatedStr,
      }, true)
    }
    partOne = interpolatedStr
    return interpolate(formatStrOnePart, {
      partOne,
    }, true)
  }

  // This shouldn't be reached normally
  return ''
}

const updateInstances = () => {
  const currentMomentUtc = moment.utc()
  for (const [, data] of instanceMap) {
    const naturalValue =
      calculateNatural(currentMomentUtc, data.momentInstance)
    data.jqElement.text(naturalValue)
  }
}

setInterval(updateInstances, 60000)

const onRemoveElement = (domNode) => {
  instanceMap.delete(domNode)
}

export function add(jqTimeElements) {
  const currentMomentUtc = moment.utc()
  for (const item of jqTimeElements) {
    const domNode = item
    const jqElement = $(domNode)
    const momentInstance = moment.utc(jqElement.attr('datetime'))
    const data = {
      jqElement,
      momentInstance,
    }
    if (!instanceMap.has(domNode)) {
      instanceMap.set(domNode, data)
      jqElement.text(calculateNatural(currentMomentUtc, momentInstance))
      jqElement.tooltip()
    }
  }
  mutationObserver.observeRemove(jqTimeElements, onRemoveElement)
}

export function init(optionsPassed) {
  for (const [key, value] of optionsPassed) {
    options[key] = optionsPassed[value]
  }
}
