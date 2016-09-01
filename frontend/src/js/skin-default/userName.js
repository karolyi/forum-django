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
  // Fill the tooltip, if any is still hovered
  if (!moduleLocals.jqUserHovered) return
  moduleLocals.jqUserHovered = undefined
}

const onXhrSuccessShortData = (result) => {
  console.debug('onXhrSuccessShortData', result)
  fillTooltip()
}

const onXhrErrorShortData = (xhr) => {
  console.debug('onXhrErrorShortData', xhr)
}


const loadUserData = (userId) => {
  // Load the user data
  $.when($.ajax({
    url: moduleLocals.options.urls.shortData.replace('12345', userId),
    dataType: 'json',
  })).then(onXhrSuccessShortData, onXhrErrorShortData)
}

const onMouseInUsername = (event) => {
  const jqUsername = $(event.currentTarget)
  moduleLocals.jqUserHovered = jqUsername
  const userId = jqUsername.data('userid')
  if (userMap.has(userId)) {
    fillTooltip()
  } else {
    loadUserData(userId)
  }
}

const onMouseOutUsername = (event) => {
  moduleLocals.jqUserHovered = undefined
}

export function init(options) {
  moduleLocals.options = options
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
