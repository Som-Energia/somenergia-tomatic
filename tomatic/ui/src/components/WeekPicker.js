import React, { useState, useEffect } from 'react'
import Tomatic from '../services/tomatic'
import styled from '@emotion/styled'

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
  const [weeks, setWeeks] = useState([])
  const [currentWeek, setCurrentWeek] = useState(Tomatic.currentWeek())

  useEffect(() => {
    setWeeks(Tomatic.weeks())
  }, [])

  const handleClick = (week) => {
    setCurrentWeek(week)
    Tomatic.requestGrid(week)
  }

  return (
    <List>
      {weeks.map((element) => {
        if (element === currentWeek) {
          return (
            <CurrentItem key={element} onClick={() => handleClick(element)}>
              {'Setmana del ' + element}
            </CurrentItem>
          )
        }
        return (
          <ListItem key={element} onClick={() => handleClick(element)}>
            {'Setmana del ' + element}
          </ListItem>
        )
      })}
    </List>
  )
}

export default WeekPicker
