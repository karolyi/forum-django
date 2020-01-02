import $ from 'jquery'
import 'bootstrap/js/src/tooltip'
import template from 'lodash/template'
import cloneDeep from 'lodash/cloneDeep'
import { DefaultWhitelist } from 'bootstrap/js/src/tools/sanitizer'
import { options as commonOptions, extractTemplateHtml } from './common'

let classInstance

class ForumUserName {
  onMouseInUsername(event) {
    const jqUsername = $(event.currentTarget)
    this.jqUserHovered = jqUsername
    const userSlug = jqUsername.data('slug')
    if (jqUsername.attr('data-is-filled') === 'true') return
    if (this.userMap.has(userSlug)) {
      this.fillTooltip()
    } else if (!this.loadedSet.has(userSlug)) {
      this.loadUserData(userSlug)
    }
  }

  onMouseOutUsername() {
    this.jqUserHovered = undefined
  }

  onXhrSuccessShortData(result) {
    for (const [userSlug, data] of Object.entries(result)) {
      this.userMap.set(userSlug, data)
    }
    this.fillTooltip()
  }

  onXhrErrorShortData() {
    // Load has failed for some reason
    if (!this.jqUserHovered) return
    this.jqUserHovered.attr(
      'title', '<span class="fa fa-chain-broken" aria-hidden="true"></span>',
    )
    this.jqUserHovered.tooltip('_fixTitle').tooltip('show')
  }

  loadUserData(userSlug) {
    // Load the user data
    this.loadedSet.add(userSlug)
    $.when($.ajax({
      url: this.userUrl({ slug: userSlug }),
      dataType: 'json',
    })).then(::this.onXhrSuccessShortData, ::this.onXhrErrorShortData)
  }

  fillTooltip() {
    // Fill the tooltip only if any username is still hovered
    if (!this.jqUserHovered) return
    const userSlug = this.jqUserHovered.data('slug')
    const userData = this.userMap.get(userSlug)
    const clonedTemplate = this.tooltipTemplate.clone()
    const ratingAvg = parseFloat(userData.rating.avg)
    userData.rating.text = userData.rating.avg
    if (ratingAvg > 0) {
      userData.rating.text = `+${userData.rating.text}`
    }
    if (userData.quote) {
      clonedTemplate.find('.quote .value').text(userData.quote)
    }
    clonedTemplate.find('.quote').toggle(!!userData.quote)
    clonedTemplate.find('.is-admin')
      .toggle(!!(userData.isSuperuser || userData.isStaff))
    clonedTemplate.find('.is-banned').toggle(userData.isBanned)
    clonedTemplate.find('.ratings .value .count').text(userData.rating.count)
    const jqAverage = clonedTemplate.find('.ratings .value .average')
    jqAverage.text(userData.rating.text)
    if (ratingAvg > 0) jqAverage.addClass('rating-positive')
    else if (ratingAvg < 0) jqAverage.addClass('rating-negative')

    // Add decoration to all the visible tr's but the first
    clonedTemplate
      .find('tr').not('[style]').not(':first').addClass('decorated')
    this.jqUserHovered
      .attr('title', clonedTemplate[0].outerHTML)
      .tooltip('_fixTitle')
      .tooltip('show')
  }

  initVariables() {
    this.tooltipTemplate = $(extractTemplateHtml(
      document.querySelector(commonOptions.selectors.user.tooltipTemplate),
    ))
    this.userMap = new Map()
    this.loadedSet = new Set()
    this.userUrl = template(
      commonOptions.urls.userShortData.backend
        .replace(commonOptions.urls.userShortData.exampleSlug, '{slug}'),
    )
    this.tooltipWhiteList = cloneDeep(DefaultWhitelist)
    // this.tooltipWhiteList['*'].push('data-toggle', 'title')
    this.tooltipWhiteList.table = ['class']
    this.tooltipWhiteList.tbody = []
    this.tooltipWhiteList.tr = ['hidden', 'class', 'style']
    this.tooltipWhiteList.td = ['colspan', 'class', 'style']
  }

  addDomElements(jqUsers) {
    jqUsers
      .attr('title', '<span class="fa fa-spinner fa-pulse fa-fw"></span>')
      .attr('data-toggle', 'tooltip')
      .tooltip({ html: true, whiteList: this.tooltipWhiteList })
      .hover(::this.onMouseInUsername, ::this.onMouseOutUsername)
  }

  constructor(options) {
    this.options = options
    this.initVariables()
  }
}

export function init(options) {
  $.when($.ready).then(() => {
    classInstance = new ForumUserName(options)
  })
}

export function add(jqUsers) {
  if (!classInstance) return
  classInstance.addDomElements(jqUsers)
}
