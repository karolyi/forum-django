/* eslint-env node:false */
/* global riot, describe, it, beforeEach, assert */

describe('Hello forum-app', () => {
  beforeEach(() => {
    // create mounting points
    const html = document.createElement('forum-app')
    document.body.appendChild(html)
  })

  it('should mount the tag', () => {
    riot.mount('forum-app')
    assert.equal(
      document.querySelector('forum-app h3').textContent,
      'This is mothafuckin JavaScript !')
  })
})

