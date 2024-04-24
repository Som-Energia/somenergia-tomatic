import { beforeEach, afterEach, describe, expect, test, it } from 'vitest'

import { vat2nif } from './vat'

describe('vat-nif conversion test', () => {
  it('remove ES from spanish VAT', () => {
    expect(vat2nif('ES12345678Z')).toBe('12345678Z')
  })
  it('same if already nif', () => {
    expect(vat2nif('12345678Z')).toBe('12345678Z')
  })
  it('same if foreign vat', () => {
    expect(vat2nif('ATU99999999')).toBe('ATU99999999')
  })
  it('if undefined return null', () => {
    expect(vat2nif(undefined)).toBe(null)
  })
  it('if falsable return null', () => {
    expect(vat2nif(false)).toBe(null)
  })
})
