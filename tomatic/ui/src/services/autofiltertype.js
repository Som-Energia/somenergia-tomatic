export default function autofiltertype(input) {
  switch (true) {
    case /@/.test(input): return 'email'
    case /^[0-9]{9}$/.test(input): return 'phone'
    case /^[0-9]{7}$/.test(input): return 'contract'
    case /^[ST]?[0-9]{1,6}$/.test(input): return 'soci'
    case /^[KLMXYZ0-9][0-9]{7}[A-HJ-NP-TV-Z0-9]$/i.test(input.toUpperCase()): return 'nif'
    case /^ES[KLMXYZ0-9][0-9]{7}[A-HJ-NP-TV-Z0-9]$/i.test(input.toUpperCase()): return 'nif'
    case /^ES[0-9]{16}[A-Z]{2}$/i.test(input): return 'cups'
    case /^ES[0-9]{16}[A-Z]{2}[0-9][FPRCXYZ]$/i.test(input): return 'cups'
    case /^[0-9]+$/.test(input): return undefined
    default: return 'name'
  }
}

