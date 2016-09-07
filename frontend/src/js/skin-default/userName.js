require('bootstrap-sass/assets/javascripts/bootstrap/tooltip')
const mutationObserver = require('./mutationObserver')
const $ = require('jquery')

const userMap = new Map()
// Fuck ES6 var unavailability
const moduleLocals = {}

// class Instance {
//   constructor(options) {
//     this.options = options
//   }

//   removeCallback(targetNode) {
//     console.log('removed', targetNode, this.options)
//   }

//   initialize() {
//     mutationObserver.observeRemove(
//       this.options.jqUsers, this.removeCallback.bind(this))
//   }
// }
const fillTooltip = () => {
  // Fill the tooltip, if any username is still hovered
  if (!moduleLocals.jqUserHovered) return
  const userSlug = moduleLocals.jqUserHovered.data('slug')
  const clonedTemplate = moduleLocals.tooltipTemplate.clone()
  const userData = userMap.get(userSlug)
  const ratingAvg = parseFloat(userData.rating.avg)
  userData.rating.text = userData.rating.avg
  if (ratingAvg > 0) {
    userData.rating.text = `+${userData.rating.text}`
  }
  if (userData.quote) {
    clonedTemplate.find('.quote .value').text(userData.quote)
    clonedTemplate.find('.quote').removeClass('hide')
  }
  if (userData.isSuperuser || userData.isStaff) {
    clonedTemplate.find('.is-admin').removeClass('hide')
  }
  if (userData.isBanned) {
    clonedTemplate.find('.is-banned').removeClass('hide')
  }
  clonedTemplate.find('.ratings .value .count').text(userData.rating.count)
  const jqAverage = clonedTemplate.find('.ratings .value .average')
  jqAverage.text(userData.rating.text)
  if (ratingAvg > 0) jqAverage.addClass('rating-positive')
  else if (ratingAvg < 0) jqAverage.addClass('rating-negative')

  // Add decoration to all the visible tr's but the first
  clonedTemplate.find('tr:not(.hide):not(:first)').addClass('decorated')

  moduleLocals.jqUserHovered.attr('title', clonedTemplate[0].outerHTML)
  moduleLocals.jqUserHovered.tooltip('fixTitle').tooltip('show')
  moduleLocals.jqUserHovered.attr('data-is-filled', true)
}

const onXhrSuccessShortData = (result) => {
  for (const [userSlug, data] of Object.entries(result)) {
    userMap.set(userSlug, data)
  }
  fillTooltip()
}

const onXhrErrorShortData = (xhr) => {
  // Load has failed for some reason
  if (!moduleLocals.jqUserHovered) return
  moduleLocals.jqUserHovered.attr(
    'title', '<span class="fa fa-chain-broken"></span>')
  moduleLocals.jqUserHovered.tooltip('fixTitle').tooltip('show')
}


const loadUserData = (userSlug) => {
  // Load the user data
  $.when($.ajax({
    url: moduleLocals.options.urls.shortData.replace(
      moduleLocals.options.urls.exampleSlug, userSlug),
    dataType: 'json',
  })).then(onXhrSuccessShortData, onXhrErrorShortData)
}

const onMouseInUsername = (event) => {
  const jqUsername = $(event.currentTarget)
  moduleLocals.jqUserHovered = jqUsername
  const userSlug = jqUsername.data('slug')
  if (jqUsername.attr('data-is-filled') === 'true') return
  if (userMap.has(userSlug)) {
    fillTooltip()
  } else {
    loadUserData(userSlug)
  }
}

const onMouseOutUsername = (event) => {
  moduleLocals.jqUserHovered = undefined
}

export function init(options) {
  moduleLocals.options = options
  $.when($.ready).then(() => {
    moduleLocals.tooltipTemplate =
      $(document.querySelector(
        moduleLocals.options.selectors.template).content.querySelector('table'))
      // $($(moduleLocals.options.selectors.template).html())
  })
}

export function add(options) {
  options.jqUsers.hover(onMouseInUsername, onMouseOutUsername)
  options.jqUsers.attr(
    'title', '<span class="fa fa-spinner fa-pulse fa-fw"></span>')
  options.jqUsers.attr('data-toggle', 'tooltip')
  options.jqUsers.tooltip({
    html: true,
  })
}
