import React from 'react'
import Tomatic from '../services/tomatic';
import Button from '@mui/material/Button';

function PersonPicker(props) {
    const { onPick } = props

    var extensions = Tomatic.persons().extensions || {};

    function pickCell(name) {
        return (
            <Button
            className={name}
            onClick={() => onPick(name)}
            >
                {Tomatic.formatName(name)}
            </Button>
        );
    };

    return (
        <div>
			{Object.keys(extensions).sort().map((name) => pickCell(name))}
        </div>
    )
}

export default PersonPicker