const MutationObserver = require('mutation-observer')
const $ = require('jquery')

const observedNodes = new Map()

const nodeRemoved = (targetNode) => {
  if (!targetNode.getElementsByTagName) return
  const everyDescendants = [...targetNode.getElementsByTagName('*')]
  for (const [observedNode, callbacks] of observedNodes) {
    if (everyDescendants.indexOf(observedNode) === -1) continue
    // The observed node is a child of the removed node
    for (let idx = 0; idx < callbacks.length; idx++) {
      const removeCallback = callbacks[idx]
      removeCallback(observedNode)
    }
    observedNodes.delete(observedNode)
  }
}

const addObserver = (targetNode, callback) => {
  if (observedNodes.has(targetNode)) {
    observedNodes.get(targetNode).push(callback)
  } else {
    observedNodes.set(targetNode, [callback])
  }
}

const watchMutate = (mutation) => {
  // Check for removed nodes
  if (mutation.type !== 'childList') {
    return
  }
  for (let idx = 0; idx < mutation.removedNodes.length; idx++) {
    const targetNode = mutation.removedNodes[idx]
    nodeRemoved(targetNode)
  }
}

$.when($.ready).then(() => {
  const observer = new MutationObserver((mutations) => {
    for (let idx = 0; idx < mutations.length; idx++) {
      watchMutate(mutations[idx])
    }
  })
  observer.observe(document.body, {
    attributes: false,
    childList: true,
    characterData: false,
    subtree: true,
  })
})

export function observeRemove(jqNode, callback) {
  for (let idx = 0; idx < jqNode.length; idx++) {
    const targetNode = jqNode[idx]
    addObserver(targetNode, callback)
  }
}

