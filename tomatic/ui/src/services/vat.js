function vat2nif(vat) {
  if (!vat) return null
  if (vat.slice(0, 2) === 'ES') return vat.slice(2)
  return vat
}

export { vat2nif }