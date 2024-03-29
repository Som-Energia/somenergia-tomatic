import m from 'mithril'
import { Card } from 'polythene-mithril-card'
import { Tabs } from 'polythene-mithril-tabs'
import CallInfo from './callinfo'

var PartnerInfo = {}

var infoPartner = function () {
  const languages = {
    ca_ES: 'Català',
    es_ES: 'Castellano',
    eu_ES: 'Euskara',
    gl_ES: 'Galego',
  }
  var partner = CallInfo.selectedPartner()
  // TODO: Move urls to an external configuration
  var helpscouturl = 'https://secure.helpscout.net/search/?query='
  var ovhijackurl = 'https://oficinavirtual.somenergia.coop/et/auth/user/?q='
  var emails = partner.email.split(',')
  var dni =
    partner.dni.slice(0, 2) === 'ES' ? partner.dni.slice(2) : partner.dni
  const markedErrorIfMissing = function (value, message) {
    return value || m('span.red', message)
  }
  return m('.partner-info', [
    m('.partner-info-item', [
      m(
        '',
        m('.label-right', [
          m('i.fa.fa-id-card', { 'aria-label': 'NIF' }),
          ' ',
          markedErrorIfMissing(dni, 'Sense NIF'),
          ' - ',
          m('i.fa.fa-id-badge', { 'aria-label': 'Codi Socia' }),
          ' ',
          partner.is_member
            ? markedErrorIfMissing(partner.id_soci, 'No codi socia')
            : m('del', partner.id_soci),
        ]),
      ),
      m('', m('.label', partner.name)),
    ]),
    m(
      '.partner-info-item',
      m('i.fa.fa-map-marker', { 'aria-label': 'Adreça' }),
      ' ',
      markedErrorIfMissing(partner.address, 'Sense adreça'),
    ),
    m(
      '.partner-info-item',
      partner.comment &&
        m(
          '.label-right.tooltip',
          m('i.fa.fa-comment', {
            'aria-label': 'Té anotacions',
          }),
          ' Té anotacions ',
          m('.tooltiptext.partner-comment', partner.comment),
        ),
      m('i.fa.fa-city', { 'aria-label': 'Municipi i Província' }),
      ' ',
      markedErrorIfMissing(partner.city, 'Sense municipi'),
      ' (',
      markedErrorIfMissing(partner.postalcode, 'Sense codi postal'),
      ') ',
      markedErrorIfMissing(partner.state, 'Sense província'),
    ),
    m(
      '.partner-info-item',
      m(
        '.label-right',
        m('i.fa.fa-grin-tongue', { 'aria-label': 'Idioma' }),
        ' ',
        markedErrorIfMissing(
          languages[partner.lang] || partner.lang,
          'Sense idioma preferent',
        ),
      ),
      emails.map(function (email) {
        return m(
          '.partner-info-item',
          m('i.fa.fa-envelope'),
          ' ',
          email,
          ' (',
          m(
            'a',
            {
              href: helpscouturl + email,
              target: '_blank',
              title: 'Cerca correus al Helpscout',
            },
            'Helpscout',
          ),
          ')',
        )
      }),
    ),
    m(
      '.partner-info-item',
      m('', m('i.fa.fa-phone'), ' ', partner.phones.join(' - ')),
    ),
    m(
      '.partner-info-item',
      partner.energetica ? m('.label-energetica', "Soci d'Energetica.") : '',
    ),
    m(
      '.partner-info-item',
      partner.is_member ||
        m('', m('i.fa.fa-eject'), ' ', m('span.red', 'Sòcia de baixa')),
    ),
    m('.partner-info-item', [
      m(
        '',
        m('.label-right', [
          m('i.fa.fa-user-secret', { 'aria-label': 'Segresta' }),
          ' (',
          m(
            'a',
            {
              href: ovhijackurl + dni,
              target: '_blank',
              title: 'Entrar a la Oficina Virtual emulant ser aquesta usuaria',
            },
            'Segrest Oficina Virtual',
          ),
          ')',
        ]),
      ),
      m(
        '',
        m('i.fa.fa-desktop', { 'aria-label': 'Oficina Virtual' }),
        ' ',
        m('.label', ' Ha obert OV? '),
        markedErrorIfMissing(partner.ov && 'Sí', 'No'),
      ),
    ]),
  ])
}

function nameFromFullName(name) {
  var parts = name.split(',')
  if (!parts[1]) {
    return name.split(' ')[0]
  }
  return parts[1]
}

function buttons(partners) {
  return partners.map(function (partner, index) {
    return {
      label: nameFromFullName(partner.name),
      selected: index === CallInfo.currentPerson,
    }
  })
}

var partnerCard = function (partners) {
  return m('.partner-card', [
    m('.partner-tabs', [
      m(Tabs, {
        selected: 'true',
        scrollable: 'true',
        all: {
          activeSelected: 'true',
          ink: 'true',
        },
        tabs: buttons(partners),
        onChange: function (ev) {
          CallInfo.selectPartner(ev.index)
          if (ev.index) {
            CallInfo.notifyUsage('callinfoChangePartner')
          }
        },
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        {
          text: {
            content: infoPartner(),
          },
        },
      ],
    }),
  ])
}

PartnerInfo.allInfo = function (info) {
  return m('.main-info-card', [partnerCard(info.partners)])
}

export default PartnerInfo
// vim: ts=2 sw=2 et
