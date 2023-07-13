import React from 'react'
import Tomatic from '../services/tomatic';
import Grid from '@mui/material/Grid';
import styled from '@emotion/styled';

function PersonPicker(props) {
    const { onPick } = props

    var extensions = Tomatic.persons().extensions || {};

    const CellItem = styled.span `
        label: name;
        cursor: pointer;
        text-align: center;
        padding: .5em;
        margin: .3em;
        :hover {
            background: #bcb;
        }
    `
    function pickCell(name) {
        return (
            <CellItem
            className = {'extension ' + name}
            onClick={() => onPick(name)}
            >
                {Tomatic.formatName(name)}
            </CellItem>
        );
    };

    return (
        <Grid style={{margin:1}} container spacing={{ xs:4, md: 4 }}>
            {Object.keys(extensions).sort().map((name) => pickCell(name))}
        </Grid>
    )
}

export default PersonPicker