import React, {useState, useEffect} from 'react'
import Tomatic from '../services/tomatic';
import styled from '@emotion/styled';


const List = styled.ul `
	label: weeks;
	display: inline-block;
	width: 100%;
`

const ListItem = styled.li `
	label: week;
	cursor: pointer;
	text-align: center;
	padding: 3px;
	color: black;
	background: #ccc;
	list-style-type:none;
	:hover {
		background: #bcb;
	}
`
const CurrentItem = styled.li `
	label: current;
	text-align: center;
	font-weight: bold;
	list-style-type:none;
	background: #7a7;
	:hover { /* week:hover would be stronger 
		background: #7a7;
	}
	:before {
		content: "►";
	}
	:after {
		content: "◄";
	}
`

function WeekPicker() {
	const [weeks, setWeeks] = useState([])
	const [currentWeek, setCurrentWeek] = useState(null)

	useEffect(() => {
		setWeeks(Tomatic.weeks())
	},[])

	const handleClick = (week) => {
		setCurrentWeek(week);
	}
  
  	return (
		<List>
		{weeks.map(element =>{
			if(element === currentWeek){
				return <CurrentItem onClick={() => handleClick(element)} >{"Setmana del " + element}</CurrentItem>
			}
			return <ListItem onClick={() => handleClick(element)} >{"Setmana del " + element}</ListItem>
		} )}
		</List>
  	)
}

export default WeekPicker

