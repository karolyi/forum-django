/* eslint-env node:false */
/* global riot, describe, it, beforeEach, assert, before */

describe('Test tag tests', () => {
  let tagNode;

  before((done) => {
    riot.compile('/base/frontend/src/js/skin-default/test.tag', () => {
      done()
    })
  })

  beforeEach(() => {
    // create mounting points
    tagNode = document.createElement('test-tag')
    document.body.appendChild(tagNode)
  })

  it('should mount the tag', () => {
    riot.mount(tagNode, 'test-tag')
    assert.equal(
      document.querySelector('test-tag i').textContent,
      'heheheh')
  })
})

