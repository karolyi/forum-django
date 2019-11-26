const MutationObserver = require('mutation-observer')
const $ = require('jquery')

const observedNodes = new Map()

const nodeRemoved = (targetNode) => {
  if (!targetNode.getElementsByTagName) return
  const everyDescendants = [...targetNode.getElementsByTagName('*')]
  for (const [observedNode, callbacks] of observedNodes) {
    if (everyDescendants.indexOf(observedNode) === -1) continue
    // The observed node is a child of the removed node
    for (const removeCallback of callbacks) removeCallback(observedNode)
    observedNodes.delete(observedNode)
  }
}

const watchMutate = (mutation) => {
  // Check for removed nodes
  if (mutation.type !== 'childList') {
    return
  }
  for (const targetNode of mutation.removedNodes) nodeRemoved(targetNode)
}

$.when($.ready).then(() => {
  const observer = new MutationObserver((mutations) => {
    for (const mutationItem of mutations) watchMutate(mutationItem)
  })
  observer.observe(document.body, {
    attributes: false,
    childList: true,
    characterData: false,
    subtree: true,
  })
})

export function observeRemoveNode(targetNode, callback) {
  if (observedNodes.has(targetNode)) {
    observedNodes.get(targetNode).push(callback)
  } else {
    observedNodes.set(targetNode, [callback])
  }
}

export function observeRemoveJq(jqNode, callback) {
  for (const targetNode of jqNode) observeRemoveNode(targetNode, callback)
}
