import React, {useState} from 'react'

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import PersonPicker from './PersonPicker';

import Tomatic from '../services/tomatic';
import Auth from '../services/auth';

function EditDialog(props){
    const { open, onClose, data, handleChange } = props
 
    var oldPerson = Tomatic.cell(data.day, data.hour, data.turn)

    const setPerson = (name) => {
        handleChange(name, data)
    }

    return (
        <div>
            <Dialog open={open}>
                <DialogTitle>Edita posició de la graella</DialogTitle>
                <DialogContent> {Tomatic.weekday(data.day) +' a les ' + Tomatic.grid().hours[data.hour] + ', línia ' + (data.turn + 1) +', la feia '} <span className={'extension ' + oldPerson}>{Tomatic.formatName(oldPerson)}</span> {'. Qui ho ha de fer?'} </DialogContent>
                <DialogContent><PersonPicker onPick={setPerson}></PersonPicker></DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel·la</Button>
                </DialogActions>
            </Dialog>
        </div>
    )
}

export default EditDialog