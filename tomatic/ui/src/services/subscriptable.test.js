import subscriptable from './subscriptable'
import { prop } from './subscriptable'

describe('subscriptable', () => {
  it('is called when notified', () => {
    let ncalls = 0
    const object = subscriptable({})
    function subscriber() {
      ncalls++
    }
    const unsubscribe = object.subscribe(subscriber)
    object.notify()
    expect(ncalls).toBe(1)
    object.notify()
    expect(ncalls).toBe(2)
    unsubscribe()
    object.notify()
    expect(ncalls).toBe(2)
  })
  it('supports multiple subscribers', () => {
    let sub1calls = 0
    let sub2calls = 0
    const object = subscriptable({})
    const subscriber1 = () => sub1calls++
    const subscriber2 = () => sub2calls++
    const unsubscribe1 = object.subscribe(subscriber1)
    const unsubscribe2 = object.subscribe(subscriber2)
    object.notify()
    expect(sub1calls).toBe(1)
    expect(sub2calls).toBe(1)
    unsubscribe1()
    object.notify()
    expect(sub1calls).toBe(1)
    expect(sub2calls).toBe(2)
  })
  it('supports functions as targets', () => {
    let ncalls = 0
    const object = subscriptable(() => {})
    function subscriber() {
      ncalls++
    }
    const unsubscribe = object.subscribe(subscriber)
    object.notify()
    expect(ncalls).toBe(1)
    object.notify()
    expect(ncalls).toBe(2)
    unsubscribe()
    object.notify()
    expect(ncalls).toBe(2)
  })
  it('propagates notify parameters', () => {
    let parameters = undefined
    const object = subscriptable({})
    function subscriber(...args) {
      parameters = args
    }
    const unsubscribe = object.subscribe(subscriber)
    object.notify('param1', 'param2')
    expect(parameters).toStrictEqual(['param1', 'param2'])
  })
})

describe('prop, subscriptable properties', () => {
  it('is set to the initial value', () => {
    const property = prop('value')
    expect(property()).toStrictEqual('value')
  })
  it('mutates after setter', () => {
    const property = prop('value')
    property('other')
    expect(property()).toStrictEqual('other')
  })
  it('is subscriptable', () => {
    const property = prop('value')
    let called = false
    property.subscribe(() => (called = true))
    expect(called).toBe(false)
    property.notify()
    expect(called).toBe(true)
  })
  it('notifies on set', () => {
    const property = prop('value')
    let called = false
    property.subscribe(() => (called = property()))
    expect(called).toBe(false)
    property('newvalue')
    expect(called).toBe('newvalue')
  })
})
