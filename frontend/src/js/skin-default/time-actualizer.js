import 'bootstrap/js/src/tooltip'
import $ from 'jquery'
import { DateTime } from 'luxon'
import { observeRemoveJq } from './mutation-observer'

window.DateTime = DateTime

class TimeActualizer {
  constructor(options) {
    this.options = options
    this.updateTime()
    this.instanceMap = new Map()
    this.strings = {
      today: this.now.toRelativeCalendar(),
      yDay: this.now.minus({ days: 1 }).toRelativeCalendar(),
      y2Day: this.now.minus({ days: 2 }).toRelativeCalendar(),
    }
    this.intervalId = setInterval(::this.updateInstances, 60000)
    this.fullFormat = {
      year: 'numeric',
      // weekday: 'long',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      // second: 'numeric',
    }
  }

  onRemoveElement(domNode) {
    this.instanceMap.delete(domNode)
  }

  updateTime() {
    this.now = DateTime.local().setLocale(this.options.languageInfo.code)
    this.isoToday = this.now.toISODate()
    this.isoYesterday =
      this.now.minus({ days: 1 }).toISODate()
    this.isoDayBeforeYesterday =
      this.now.minus({ days: 2 }).toISODate()
  }

  updateOneInstance(data) {
    const { jqElement, luxonInstance } = data
    const isoDate = luxonInstance.toISODate()
    console.debug('XXX', jqElement[0], isoDate, this.isoToday)
    if (isoDate === this.isoToday) {
      const formattedTime = luxonInstance.toLocaleString(DateTime.TIME_SIMPLE)
      jqElement.text(`${this.strings.today}, ${formattedTime}`)
    } else if (isoDate === this.isoYesterday) {
      const formattedTime = luxonInstance.toLocaleString(DateTime.TIME_SIMPLE)
      jqElement.text(`${this.strings.yDay}, ${formattedTime}`)
    } else if (isoDate === this.isoDayBeforeYesterday) {
      const formattedTime = luxonInstance.toLocaleString(DateTime.TIME_SIMPLE)
      jqElement.text(`${this.strings.y2Day}, ${formattedTime}`)
    } else {
      jqElement.text(luxonInstance.toLocaleString(this.fullFormat))
    }
    jqElement.attr('data-original-title', luxonInstance.toRelative({
      style: 'long',
    }))
  }

  updateInstances(newInstancesMap) {
    this.updateTime()
    const instanceMap = newInstancesMap || this.instanceMap
    for (const data of instanceMap.values()) this.updateOneInstance(data)
  }

  add(jqTimeElements) {
    const newInstancesMap = new Map()
    for (const domNode of jqTimeElements) {
      const jqElement = $(domNode)
      const luxonInstance = DateTime.fromISO(jqElement.attr('datetime'))
      if (!this.instanceMap.has(domNode)) {
        this.instanceMap.set(domNode, { jqElement, luxonInstance })
        newInstancesMap.set(domNode, { jqElement, luxonInstance })
        jqElement.tooltip()
      }
    }
    this.updateInstances(newInstancesMap)
    observeRemoveJq(jqTimeElements, ::this.onRemoveElement)
  }
}

let timeActualizer

export function init(options) {
  timeActualizer = new TimeActualizer(options)
}

export function add(jqTimeElements) {
  $.when($.ready).then(() => {
    timeActualizer.add(jqTimeElements)
  })
}
