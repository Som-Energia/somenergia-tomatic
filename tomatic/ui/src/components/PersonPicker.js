import React from 'react'
import Tomatic from '../services/tomatic';
import Grid from '@mui/material/Grid';
import styled from '@emotion/styled';

function PersonPicker(props) {
    const { onPick, nobodyPickable } = props

    var extensions = Tomatic.persons().extensions || {}

    console.log("extensions",extensions)
    const CellItem = styled.span `
        label: name;
        cursor: pointer;
        text-align: center;
        padding: .5em;
        width: 8em;
        margin: .3em;
        :hover {
            background: #bcb;
        }
    `
    const CellItemNingu = styled.span `
        label: name;
        cursor: pointer;
        text-align: center;
        padding: .5em 3em .5em 3em;
        width: 8em;
        margin: .3em;
        :hover {
            background: #bcb;
        }
    `

    function pickCell(name) {
        if (name === 'ningu')
        {
            return (
                <CellItemNingu
                className = {'extension ' + name}
                onClick={() => onPick(name)}
                >
                    {Tomatic.formatName(name)}
                </CellItemNingu>
            );
        } else {
            return (
                <CellItem
                className = {'extension ' + name}
                onClick={() => onPick(name)}
                >
                    {Tomatic.formatName(name)}
                </CellItem>
            );
        }
    };

    return (
        <Grid style={{margin:1}} container spacing={{ xs:4, md: 4 }}>
            {Object.keys(extensions).sort().map((name) => pickCell(name))}
            {nobodyPickable ? pickCell('ningu'):[]}
        </Grid>
    )
}

export default PersonPicker