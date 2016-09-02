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
  clonedTemplate.find('.quote .value').text(userData.quote)
  if (!userData.isSuperuser && !userData.isStaff) {
    clonedTemplate.find('.is-admin').addClass('hide')
  }
  moduleLocals.jqUserHovered.attr('title', clonedTemplate[0].outerHTML)
  moduleLocals.jqUserHovered.tooltip('fixTitle').tooltip('show')
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
      $(moduleLocals.options.selectors.template).remove().removeClass('hide')
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
