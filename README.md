<a href="https://www.ccma.cat/tv3/alacarta/la-meva-infantils/tomatic-club-super-3/video/4586233/">
<img
title="Tomàtic, a chatting tomato-answering machine. Until 2006, it featured on 'Club Super3', a show for kids aired by the catalan public TV. Tomàtic, alledgedly, has been working at Som Energia since 2015."
src="doc/tomatic.jpg" align='right'
/>
</a>

[![CI Status](https://github.com/Som-Energia/somenergia-tomatic/actions/workflows/main.yml/badge.svg)](https://github.com/Som-Energia/somenergia-tomatic/actions/workflows/main.yml)
[![Build Status](https://app.travis-ci.com/Som-Energia/somenergia-tomatic.svg?branch=master)](https://app.travis-ci.com/Som-Energia/somenergia-tomatic)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/somenergia-tomatic/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/somenergia-tomatic?branch=master)

# Som Energia's Tomàtic
**The coolest companion of phone attention crew  at Som Energia**



- [Features](#features): What it does
- [Setup](doc/setup.md): How to setup
- [Command Line Tools](doc/cli-tools.md): Operator guide
- [Developing](doc/development.md): Developing Tomàtic
- [TODO.md](TODO.md): Pending task list
- [CHANGES.md](CHANGES.md): Version history and change log
- [doc](docs) Further documentation (Including project requirements, glossary and designs)


## Features

This software is used within SomEnergia cooperative to improve the quality of the phone support we give to our members and clients.

- **It distributes helpline turns among the staff**

	Each week it decides the turns each person will be attending to the phone.
	Takes into account a provided ideal load for every one, their holidays, meetings,
	and some nice restrictions to ensure **staff wellbeing** and **service quality**.

- **Manual edition of the resulting time table**

	Unscheduled meetings and other events, often makes the computed timetable outdated.
	The web interface can be used to swap turns on the timetable and keep track of the changes.

- **Programming Asterisk queues according the timetable**

	Every turn, Tomàtic automatically setups the PBX queue according to the timetable.
	It sends friendly reminders to the people on duty and
	warns the coordinators whenever an agent is not connected to the PBX
	because of technical or human memory issues.

- **Realtime control of the current queue***

	You can pause agents to adapt to temporary absences,
	or adding more agents in case of bursts of incomming calls.
	Tomatic visually shows the state of each extension in the queue:
	Available, attending a call, disconnected, paused...

- **Instant information about the incomming call**

	For each incomming call, Tomàtic retrieves all the information
	in our ERP related to that number and displays it
	to the agents in an accessible format:
	contracts, invoices, alerts, previous notes...
	this way agents can resolve calls faster and better.
	If the phone is not in the database,
	still the agent can perform searches using many criteria.

- **Integrated call annotation**

	With a few clicks you can annotate current and past calls.
	Such annotations can be used to start an official claim procedure
	or just to keeps some stats that will help to improve the quality of service.

- **Tomàtic impersonation**

	Turn team coordination messages into a smile by impersonating Tomàtic
	in the chat group. It seems an amusement feature but, keeping a smile
	in our faces makes our service also nicer.





