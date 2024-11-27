import React from 'react'
import Box from '@mui/material/Box'
import CallInfo from '../../contexts/callinfo'
import TabbedCard from './TabbedCard'
import { useSubscriptable } from '../../services/subscriptable'

function nameFromFullName(name) {
  var parts = name.split(',')
  if (!parts[1]) {
    return name.split(' ')[0]
  }
  return parts[1]
}

function zeropad(value, num) {
  if (!value) return value
  return (value + '').padStart(num, '0')
}

function IconLabel({ icon, label }) {
  return <i className={icon.split('.').join(' ')} aria-label={label} />
}

function InfoLine({ ...rest }) {
  return <Box className="partner-info-item" {...rest} />
}

function PartnerContent() {
  const languages = {
    ca_ES: 'Català',
    es_ES: 'Castellano',
    eu_ES: 'Euskara',
    gl_ES: 'Galego',
  }
  const partner = useSubscriptable(CallInfo.selectedPartner)
  // TODO: Move urls to an external configuration
  const freescouturl = 'https://freescout.somenergia.coop/search?q='
  const ovhijackurl = 'https://oficinavirtual.somenergia.coop/et/auth/user/?q='
  const emails = partner.email.split(',')
  const dni =
    partner.dni.slice(0, 2) === 'ES' ? partner.dni.slice(2) : partner.dni
  const markedErrorIfMissing = function (value, message) {
    return value || <span className="red">{message}</span>
  }
  return (
    <Box className="partner-info">
      <InfoLine>
        <Box>
          <Box>
            <Box className="label-right">
              <IconLabel icon="fa.fa-id-card" label="NIF" />{' '}
              {markedErrorIfMissing(dni, 'Sense NIF')}
              {' - '}
              <IconLabel icon="fa.fa-id-badge" label="Codi Socia" />{' '}
              {partner.is_member || partner.id_soci[0] !== 'S' ? (
                markedErrorIfMissing(partner.id_soci, 'No codi socia')
              ) : (
                <del>{partner.id_soci}</del>
              )}
            </Box>
          </Box>
        </Box>
        <Box>
          <Box className="label">{partner.name}</Box>
        </Box>
      </InfoLine>
      <InfoLine>
        <IconLabel icon="fa.fa-map-marker" label="Adreça" />{' '}
        {markedErrorIfMissing(partner.address, 'Sense adreça')}
      </InfoLine>
      <InfoLine>
        {partner.comment && (
          <Box className="label-right tooltip">
            <IconLabel icon="fa.fa-comment" label="Té anotacions" />
            {' Té anotacions '}
            <Box className="tooltiptext partner-comment">{partner.comment}</Box>
          </Box>
        )}
        <IconLabel icon="fa.fa-city" label="Municipi i Província" />{' '}
        {markedErrorIfMissing(partner.city, 'Sense municipi')}
        {' ('}
        {markedErrorIfMissing(
          zeropad(partner.postalcode, 5),
          'Sense codi postal',
        )}
        {') '}
        {markedErrorIfMissing(partner.state, 'Sense província')}
      </InfoLine>
      <InfoLine>
        <Box className="label-right">
          <IconLabel icon="fa.fa-grin-tongue" label="Idioma" />{' '}
          {markedErrorIfMissing(
            languages[partner.lang] || partner.lang,
            'Sense idioma preferent',
          )}
        </Box>
        {emails.map(function (email, i) {
          return (
            <Box className="partner-info-item" key={i}>
              <IconLabel icon="fa.fa-envelope" label="Email" /> {email} (
              <a
                href={freescouturl + email}
                target="_blank"
                rel="noreferrer"
                title="Cerca correus al FreeScout"
              >
                FreeScout
              </a>
              )
            </Box>
          )
        })}
      </InfoLine>
      <InfoLine>
        <IconLabel icon="fa.fa-phone" /> {partner.phones.join(' - ')}
      </InfoLine>
      {partner.energetica ? (
        <InfoLine>
          <Box className="label-energetica">{"Soci d'Energetica."}</Box>
        </InfoLine>
      ) : null}
      {!partner.is_member ? (
        <Box>
          <IconLabel icon="fa.fa-eject" />{' '}
          <span className="red">{'Sòcia de baixa'}</span>
        </Box>
      ) : null}
      <InfoLine>
        <Box className="label-right">
          <IconLabel icon="fa.fa-user-secret" label="Segresta" />
          {' ('}
          <a
            href={ovhijackurl + dni}
            target="blanc_"
            title="Entrar a la Oficina Virtual emulant ser aquesta usuaria"
          >
            {'Segrest Oficina Virtual'}
          </a>
          )
        </Box>
        <Box>
          <IconLabel icon="fa.fa-desktop" label="Oficina Virtual" />{' '}
          <Box className="label">{' Ha obert OV? '}</Box>
          {markedErrorIfMissing(partner.ov && 'Sí', 'No')}
        </Box>
      </InfoLine>
    </Box>
  )
}

export default function PartnerInfo() {
  const { partners } = CallInfo.results.use()
  // TODO: Ignored, just needed to get update when index change
  const partner = useSubscriptable(CallInfo.selectedPartner)
  if (!partner) return

  function onTabChanged(value) {
    CallInfo.selectPartner(value)
    CallInfo.notifyUsage('callinfoChangePartner')
  }
  return (
    <Box className="main-info-card">
      <TabbedCard
        currentTab={CallInfo.currentPerson}
        onTabChanged={onTabChanged}
        labels={partners.map((partner) => nameFromFullName(partner.name))}
        Inner={PartnerContent}
      />
    </Box>
  )
}
