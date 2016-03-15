/* eslint-env node:false */
/* global riot, describe, it, beforeEach, assert, before */

describe('Forum tag tests', () => {
  let tagNode
  before((done) => {
    riot.compile('/base/frontend/src/js/skin-default/index.tag', () => {
      done()
    })
  })

  beforeEach(() => {
    // create mounting points
    tagNode = document.createElement('forum-app')
    document.body.appendChild(tagNode)
  })

  it('should mount the tag', () => {
    riot.mount(tagNode, 'forum-app')
    assert.equal(
      document.querySelector('forum-app h3').textContent,
      'This is mothafuckin JavaScript !')
    assert.equal(document.querySelector('forum-app test-tag').innerHTML, '')
  })
})


