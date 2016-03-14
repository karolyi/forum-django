const fs = require('fs')
// const util = require('util')
const path = require('path')

// Prepare a production head tag with the loader script
exports.createBundleLoader = () => {
  const bundleContent = fs.readFileSync(path.resolve(path.join(
    __dirname, '..', '..', '..', 'dist', 'assets', 'stats.json')), 'utf-8')
  const bundleParsed = JSON.parse(bundleContent)
  console.log('bundleParsed', bundleParsed)
}
