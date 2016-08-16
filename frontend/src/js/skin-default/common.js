exports.options = {}

exports.init = (optionsPassed) => {
  let key
  for (key of Object.keys(optionsPassed)) {
    exports.options[key] = optionsPassed[key]
  }
}
