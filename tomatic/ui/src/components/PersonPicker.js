import React from 'react'
import Tomatic from '../services/tomatic';
import Button from '@mui/material/Button';

function PersonPicker(props) {
    const { onPick } = props

    var extensions = Tomatic.persons().extensions || {};

    function pickCell(name) {
        return (
            <span
            className={'extension ' + name}
            onClick={() => onPick(name)}
            >
                {Tomatic.formatName(name)}
            </span>
        );
    };

    return (
        <div className='extensions'>
			{Object.keys(extensions).sort().map((name) => pickCell(name))}
        </div>
    )
}

export default PersonPicker