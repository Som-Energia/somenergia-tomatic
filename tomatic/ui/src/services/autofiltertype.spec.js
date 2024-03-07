import autofiltertype from './autofiltertype'

function no() {}

describe('autofiltertype detects which kind of searc we are doing', () => {
  it('has nine numbers, should be a phone', () => {
    expect(autofiltertype('123456789')).toBe('phone')
  })
  it('has seven numbers, should be a contract', () => {
    expect(autofiltertype('1234567')).toBe('contract')
  })
  it('has less than seven numbers, should be a member', () => {
    expect(autofiltertype('123456')).toBe('soci')
  })
  it('has a S prefix and less than seven numbers, should be a member', () => {
    expect(autofiltertype('S123456')).toBe('soci')
  })
  it('has more than 9 numbers, is unknown', () => {
    expect(autofiltertype('1234567890')).toBe(undefined)
  })
  it('has @, should be email', () => {
    expect(autofiltertype('a@a.net')).toBe('email')
  })
  it('has eight numbers and a control letter, should be a dni, specific kind of a nif', () => {
    expect(autofiltertype('12345678Z')).toBe('nif')
  })
  it('has a letter seven numbers and a control letter, should be a nif', () => {
    expect(autofiltertype('K1234567Z')).toBe('nif')
  })
  it('is a lower cased nif, should also be a nif', () => {
    expect(autofiltertype('K1234567Z')).toBe('nif')
  })
  it('is a lower cased nif, should also be a nif', () => {
    expect(autofiltertype('ESK1234567Z')).toBe('nif')
  })
  it('has mostly letters, a name', () => {
    expect(autofiltertype('Pepito')).toBe('name')
  })
  it('has cups structure, a cups', () => {
    expect(autofiltertype('ES1234123456789012JY')).toBe('cups')
  })
  it('has cups structure lowercase, a cups', () => {
    expect(autofiltertype('es1234123456789012jy')).toBe('cups')
  })
})
