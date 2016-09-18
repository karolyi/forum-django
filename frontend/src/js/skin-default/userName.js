require('bootstrap/js/src/tooltip')
const $ = require('jquery')

const userMap = new Map()
// Fuck ES6 var unavailability
const moduleLocals = {}

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
  clonedTemplate.find('tr:not(.hide):not(:first)').addClass('decorated')

  moduleLocals.jqUserHovered.attr('title', clonedTemplate[0].outerHTML)
  moduleLocals.jqUserHovered.tooltip('_fixTitle').tooltip('show')
  moduleLocals.jqUserHovered.attr('data-is-filled', true)
}

const onXhrSuccessShortData = (result) => {
  for (const [userSlug, data] of Object.entries(result)) {
    userMap.set(userSlug, data)
  }
  fillTooltip()
}

const onXhrErrorShortData = () => {
  // Load has failed for some reason
  if (!moduleLocals.jqUserHovered) return
  moduleLocals.jqUserHovered.attr(
    'title', '<span class="fa fa-chain-broken"></span>')
  moduleLocals.jqUserHovered.tooltip('_fixTitle').tooltip('show')
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

const onMouseOutUsername = () => {
  moduleLocals.jqUserHovered = undefined
}

export function init(options) {
  moduleLocals.options = options
  $.when($.ready).then(() => {
    moduleLocals.tooltipTemplate =
      $(document.querySelector(moduleLocals.options.selectors.template)
        .content.querySelector('table').outerHTML)
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
