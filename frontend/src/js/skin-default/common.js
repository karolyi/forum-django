const $ = require('jquery')

export const options = {
  /* eslint-disable new-cap */
  promiseWindowLoad: $.Deferred(),
  /* eslint-enable new-cap */
}

$(window).on('load', () => {
  options.promiseWindowLoad.resolve()
})

export function init(optionsPassed) {
  for (const key of Object.keys(optionsPassed)) {
    options[key] = optionsPassed[key]
  }
}

const calcNavbarHeight = () => {
  // Calculate navbar height
  const cssNavbarHeight = $(options.selectors.navbar).css('height')
  options.navbarHeight = Math.ceil(parseFloat(cssNavbarHeight.split('px')[0]))
  console.debug('cssNavbarHeight', cssNavbarHeight, options.navbarHeight)
}

$.when($.ready).then(() => {
  calcNavbarHeight()
})
