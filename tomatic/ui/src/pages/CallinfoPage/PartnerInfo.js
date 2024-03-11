import React from 'react'
import Box from '@mui/material/Box'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CallInfo from '../../mithril/components/callinfo'

function nameFromFullName(name) {
  var parts = name.split(',')
  if (!parts[1]) {
    return name.split(' ')[0]
  }
  return parts[1]
}

function Fa({ icon, ...rest }) {
  return <i className={icon.split('.').join(' ')} {...rest} />
}

function InfoLine({ ...rest }) {
  return <Box className="partner-info-item" {...rest} />
}

function Info() {
  const languages = {
    ca_ES: 'Català',
    es_ES: 'Castellano',
    eu_ES: 'Euskara',
    gl_ES: 'Galego',
  }
  const partner = CallInfo.selectedPartner()
  // TODO: Move urls to an external configuration
  const helpscouturl = 'https://secure.helpscout.net/search/?query='
  const ovhijackurl = 'https://oficinavirtual.somenergia.coop/hijack/username/'
  const emails = partner.email.split(',')
  const dni =
    partner.dni.slice(0, 2) === 'ES' ? partner.dni.slice(2) : partner.dni
  const markedErrorIfMissing = function (value, message) {
    return value || <span className="red">{message}</span>
  }
  return (
    <>
      <InfoLine>
        <Box>
          <Box>
            <Box className="label-right">
              <Fa icon="fa.fa-id-card" ariaLabel="NIF" />{' '}
              {markedErrorIfMissing(dni, 'Sense NIF')}
              {' - '}
              <Fa icon="fa.fa-id-badge" ariaLabel="Codi Socia" />{' '}
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
        <Fa icon="fa.fa-map-marker" ariaLabel="Adreça" />{' '}
        {markedErrorIfMissing(partner.address, 'Sense adreça')}
      </InfoLine>
      <InfoLine>
        {partner.comment && (
          <Box className="label-right tooltip">
            <Fa icon="fa.fa-comment" ariaLabel="Té anotacions" />
            {' Té anotacions '}
            <Box className="tooltiptext partner-comment">{partner.comment}</Box>
          </Box>
        )}
        <Fa icon="fa.fa-city" ariaLabel="Municipi i Província" />{' '}
        {markedErrorIfMissing(partner.city, 'Sense municipi')}
        {' ('}
        {markedErrorIfMissing(partner.postalcode, 'Sense codi postal')}
        {') '}
        {markedErrorIfMissing(partner.state, 'Sense província')}
      </InfoLine>
      <InfoLine>
        <Box className="label-right">
          <Fa icon="fa.fa-grin-tongue" ariaLabel="Idioma" />{' '}
          {markedErrorIfMissing(
            languages[partner.lang] || partner.lang,
            'Sense idioma preferent',
          )}
        </Box>
        {emails.map(function (email) {
          return (
            <Box className="partner-info-item">
              <Fa icon="fa.fa-envelope" ariaLabel="Email" /> {email} (
              <a
                href={helpscouturl + email}
                target="_blank"
                title="Cerca correus al Helpscout"
              >
                Helpscout
              </a>
              )
            </Box>
          )
        })}
      </InfoLine>
      <InfoLine>
        <Fa icon="fa.fa-phone" /> {partner.phones.join(' - ')}
      </InfoLine>
      {partner.energetica ? (
        <InfoLine>
          <Box className="label-energetica">{"Soci d'Energetica."}</Box>
        </InfoLine>
      ) : null}
      {!partner.is_member ? (
        <Box>
          <Fa icon="fa.fa-eject" />{' '}
          <span className="red">{'Sòcia de baixa'}</span>
        </Box>
      ) : null}
      <InfoLine>
        <Box className="label-right">
          <Fa icon="fa.fa-user-secret" ariaLabel="Segresta" />
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
          <Fa icon="fa.fa-desktop" ariaLabel="Oficina Virtual" />{' '}
          <Box className="label">{' Ha obert OV? '}</Box>
          {markedErrorIfMissing(partner.ov && 'Sí', 'No')}
        </Box>
      </InfoLine>
    </>
  )
}

export default function PartnerInfo({
  data,
  currentPartner,
  setCurrentPartner,
}) {
  function handleClick(value) {
    setCurrentPartner(value)
    CallInfo.selectPartner(value)
    CallInfo.notifyUsage('callinfoChangePartner')
  }
  const partners = data.partners
  return (
    <Box className="main-info-card">
      <Box
        className="partner-card"
        sx={{
          maxWidth: '465px',
          minWidth: '200px',
        }}
      >
        <Box className="partner-tabs">
          <Tabs
            variant="scrollable"
            scrollButtons="auto"
            dense
            value={currentPartner}
            onChange={(ev, value) => handleClick(value)}
          >
            {partners.map((partner, i) => {
              return (
                <Tab
                  key={partner.id}
                  label={nameFromFullName(partner.name)}
                  sx={{
                    '&.Mui-selected': {
                      color: '#555',
                      bgcolor: '#ABD0AB',
                    },
                  }}
                />
              )
            })}
          </Tabs>
        </Box>
        <Card className="card-info">
          <CardContent>
            <Box className="partner-info">
              <Info />
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}
