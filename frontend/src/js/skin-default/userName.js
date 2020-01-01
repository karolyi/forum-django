import $ from 'jquery'
import 'bootstrap/js/src/tooltip'
import template from 'lodash/template'
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
    } else {
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
      'title', '<span class="fa fa-chain-broken"></span>',
    )
    this.jqUserHovered.tooltip('_fixTitle').tooltip('show')
  }

  loadUserData(userSlug) {
    // Load the user data
    $.when($.ajax({
      url: this.userUrl({ slug: userSlug }),
      dataType: 'json',
    })).then(::this.onXhrSuccessShortData, ::this.onXhrErrorShortData)
  }

  fillTooltip() {
    // Fill the tooltip, if any username is still hovered
    if (!this.jqUserHovered) return
    const userSlug = this.jqUserHovered.data('slug')
    const clonedTemplate = this.tooltipTemplate.clone()
    const userData = this.userMap.get(userSlug)
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
    clonedTemplate.find('tr').not('[style]').not(':first').addClass('decorated')

    this.jqUserHovered.attr('title', clonedTemplate[0].outerHTML)
    this.jqUserHovered.tooltip('_fixTitle').tooltip('show')
    this.jqUserHovered.attr('data-is-filled', true)
  }

  initVariables() {
    this.tooltipTemplate = extractTemplateHtml(
      document.querySelector(commonOptions.selectors.user.tooltipTemplate),
    )
    this.userMap = new Map()
    this.userUrl = template(
      commonOptions.urls.userShortData.backend
        .replace(commonOptions.urls.userShortData.exampleSlug, '{slug}'),
    )
  }

  addDomElements(jqUsers) {
    jqUsers
      .attr('title', '<span class="fa fa-spinner fa-pulse fa-fw"></span>')
      .attr('data-toggle', 'tooltip')
      .tooltip({ html: true })
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
