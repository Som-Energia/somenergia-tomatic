export function preferedWeek(weeks, now = new Date()) {
  if (!weeks) return undefined
  // A time table is expired beyond its friday at 18:00
  // That is 4 days and 18 hours after monday at 00:00 (local)
  const expirationms = 1000 * 60 * 60 * (24 * 4 + 18)
  const tzoffset = now.getTimezoneOffset() * 60 * 1000
  // Instead of moving each monday and compare them to now,
  // we move now once and compare it with each monday
  const limitDate = new Date(now.getTime() - expirationms - tzoffset)
  const expireDate = limitDate.toISOString().slice(0, 10)
  return weeks.sort().reduce((result, candidate) => {
    if (result >= expireDate) return result
    return candidate
  }, undefined)
}
