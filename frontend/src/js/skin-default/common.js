const $ = require('jquery')

export const options = {}

export function init(optionsPassed) {
  for (const key of Object.keys(optionsPassed)) {
    exports.options[key] = optionsPassed[key]
  }
}

const calcNavbarHeight = () => {
  // Calculate navbar height
  const cssNavbarHeight = $(options.selectors.navbar).css('height')
  options.navbarHeight = parseInt(cssNavbarHeight.split('px')[0], 10)
}

$.when($.ready).then(() => {
  calcNavbarHeight()
})
