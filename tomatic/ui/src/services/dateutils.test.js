import { preferedWeek } from './dateutils'

describe('preferedWeek', () => {
  const w1 = '2020-01-06'
  const w2 = '2020-01-13'
  const w3 = '2020-01-20'
  const w4 = '2020-01-27'
  const w5 = '2020-01-27'
  const fridayW3 = new Date('2020-01-25')
  const fridayW3pre = new Date('2020-01-25T17:59:59')
  const fridayW3post = new Date('2020-01-25T18:00:00')

  it('returns undefined if undefined', () => {
    expect(preferedWeek(undefined, fridayW3)).toBe(undefined)
  })
  it('returns undefined if no weeks', () => {
    expect(preferedWeek([], fridayW3)).toBe(undefined)
  })
  it('chooses single week', () => {
    expect(preferedWeek([w1], fridayW3)).toBe(w1)
  })
  it('chooses latest in the past', () => {
    expect(preferedWeek([w1, w2], fridayW3)).toBe(w2)
  })
  it('chooses latest in the past, regardles the order', () => {
    expect(preferedWeek([w2, w1], fridayW3)).toBe(w2)
  })
  it('chooses earliest in the future', () => {
    expect(preferedWeek([w4, w5], fridayW3)).toBe(w4)
  })
  it('chooses earliest in the future, regardless the order', () => {
    expect(preferedWeek([w5, w4], fridayW3)).toBe(w4)
  })
  it('chooses future, among past and future', () => {
    expect(preferedWeek([w2, w4], fridayW3)).toBe(w4)
  })
  it('current week is prefered', () => {
    expect(preferedWeek([w2, w3, w4], fridayW3)).toBe(w3)
  })
  it('after working hours, choose next week', () => {
    expect(preferedWeek([w2, w3, w4], fridayW3post)).toBe(w4)
  })
  it('within working hours, choose this week', () => {
    expect(preferedWeek([w2, w3, w4], fridayW3pre)).toBe(w3)
  })
})
