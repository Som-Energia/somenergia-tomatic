import IconButton from '@mui/material/IconButton'
import { useDialog } from '../../components/DialogProvider'
import CallInfo from '../../contexts/callinfo'
import Auth from '../../services/auth'
import TypificationDialog from './TypificationDialog'
import ContentPasteIcon from '@mui/icons-material/ContentPaste'

export default function AnnotationButton() {
  const [openDialog, closeDialog] = useDialog()

  return (
    <IconButton
      title={'Anota la trucada seleccionada fent servir aquest contracte'}
      onClick={() => {
        const oldAutoRefresh = CallInfo.autoRefresh()
        CallInfo.autoRefresh(false)
        function onClose() {
          CallInfo.autoRefresh(oldAutoRefresh)
          closeDialog()
        }
        openDialog({
          maxWidth: 'md',
          children: <TypificationDialog onClose={onClose} />,
          onClose: onClose,
        })
      }}
      disabled={CallInfo.savingAnnotation || Auth.username() === ''}
    >
      <ContentPasteIcon className="icon-clipboard" />
    </IconButton>
  )
}


