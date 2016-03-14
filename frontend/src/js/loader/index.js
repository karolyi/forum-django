/* global __assetData */

const { insertScript, insertStylesheet } = require('./inserters')

const skinType = 'default'

for (const source of __assetData.skin[skinType]) {
  if (source.endsWith('.js')) {
    insertScript(source)
    continue
  }
  if (source.endsWith('.css')) {
    insertStylesheet(source)
  }
}
