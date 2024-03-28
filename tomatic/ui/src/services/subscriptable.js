import React from 'react'

/**
 * Makes an object or function subscriptable by adding methods and members
 * to handle subscriptions.
 *
 * - subscribe(callback) will subscribe the callback to the target
 * - notify(..args)  will call all subscriber callbacks with the given args
 */
export default function subscriptable(target) {
  target._subscribers = new Set()
  target.subscribe = (subscriber) => {
    target._subscribers.add(subscriber)
    return () => target._subscribers.delete(subscriber)
  }
  target.notify = (...args) => {
    target._subscribers.forEach((subscriber) => subscriber(...args))
  }
  return target
}

function callOrSelf(target, ...args) {
  if (typeof target === 'function') return target(...args)
  return target
}

/**
 * React hook to call a subscriptable
 * whenever the subscriptable is notified with notify().
 * If the subscriptable is a function it will be called with args
 * to obtain the new state, if not a function, the subscriptable
 * is the resulting state.
 */
export function useSubscriptable(target, ...args) {
  const [getter, setter] = React.useState(callOrSelf(target, ...args))
  React.useEffect(() => {
    const unsubscribe = target.subscribe(() =>
      setter(callOrSelf(target, ...args)),
    )
    return unsubscribe
  }, [target, args])
  return getter
}

export function prop(initialValue) {
  let value = initialValue
  function accessor(...args) {
    if (!args.length) return value
    value = args[0]
    accessor.notify()
  }
  accessor.use = function useProp() {
    return useSubscriptable(accessor)
  }
  subscriptable(accessor)
  return accessor
}


