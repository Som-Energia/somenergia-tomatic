import React from 'react'
import styled from '@emotion/styled'
import Tomatic from '../services/tomatic'

const List = styled.ul`
  label: weeks;
  display: inline-block;
  width: 100%;
  padding: 0px;
  margin-top: 0;
`

const ListItem = styled.li`
  label: week;
  cursor: pointer;
  text-align: center;
  padding: 3px;
  color: black;
  background: #ccc;
  list-style-type: none;
  :hover {
    background: #bcb;
  }
`
const CurrentItem = styled.li`
  label: current;
  text-align: center;
  font-weight: bold;
  list-style-type: none;
  background: #7a7;
  :hover {
    background: #7a7;
  }
  :before {
    content: '►';
    margin-inline: 0.5rem;
  }
  :after {
    margin-inline: 0.5rem;
    content: '◄';
  }
`
function WeekPicker() {
  const weeks = Tomatic.weeks.use()
  const currentWeek = Tomatic.currentWeek.use()
  return (
    <List>
      {weeks.map((week) => {
        const Item = week === currentWeek ? CurrentItem : ListItem
        return (
          <Item key={week} onClick={() => Tomatic.currentWeek(week)}>
            {'Setmana del ' + week}
          </Item>
        )
      })}
    </List>
  )
}

export default WeekPicker
