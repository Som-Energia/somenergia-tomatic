function hex2triplet(hex) {
  hex = String(hex).replace(/[^0-9a-f]/gi, '')
  if (hex.length < 6) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]
  }
  return [hex.substr(0, 2), hex.substr(2, 2), hex.substr(4, 2)].map(function (
    part,
  ) {
    return parseInt(part, 16)
  })
}
function triplet2hex(triplet) {
  var rgb = ''
  for (var i in triplet) {
    var c = triplet[i]
    var newc = Math.round(Math.min(Math.max(0, c), 255))
    rgb += ('00' + newc.toString(16)).slice(-2)
  }
  return rgb
}
function contrast(hexrgb) {
  var cs = hex2triplet(hexrgb)
  return +cs[0] * 0.429 + // R
    cs[1] * 0.557 + // G
    cs[2] * 0.014 > // B
    86
    ? 'black'
    : 'white'
}
function luminance(hex, lum) {
  var triplet = hex2triplet(hex)
  lum = lum || 0
  return triplet2hex(
    triplet.map(function (c) {
      return c + c * lum
    }),
  )
}

export { luminance, triplet2hex, hex2triplet, contrast }
