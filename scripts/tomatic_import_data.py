import sys
import subprocess
from enum import Enum, auto
import typer
from consolemsg import step
from typing_extensions import Annotated
from tomatic.remote import Remote

class Data(str, Enum):
    timetables = 'timetables'
    busy = 'busy'
    oneshot = 'oneshot'
    holidays = 'holidays'
    fixedturns = 'fixedturns'
    all = 'all'

available_data = [
    ({Data.all, Data.busy},
        'indisponibilitats.conf', '.'),
    ({Data.all, Data.oneshot},
        'oneshot.conf', '.'),
    ({Data.all, Data.holidays},
        'holidays.conf', '.'),
    ({Data.all, Data.fixedturns},
        'forced-turns.yaml', 'data'),
    ({Data.all, Data.timetables},
        'graelles', '.'),
]

def main(
        user: str,
        server: str,
        port: int,
        datum: Annotated[
            list[Data],
            typer.Argument(),
        ],
        password: Annotated[
            str,
            typer.Option(prompt=True, hide_input=True),
        ],
        path: str = '/opt/www/somenergia-tomatic',
):
    """Imports Tomatic data from another server"""
    datum = set(datum)
    path = '/opt/www/somenergia-tomatic'
    for selector, file, target in available_data:
        if selector & datum:
            cmd = f'sshpass -p "{password}" scp -r -P {port} "{user}@{server}:/opt/www/somenergia-tomatic/{file}" "{target}"'
            step(cmd)
            subprocess.run(
                args = [
                    'sshpass',
                    '-p', password,
                    'scp', '-r', '-P', str(port),
                    f'{user}@{server}:{path}/{file}',
                    target,
                ],
                stdout=sys.stdout,
                stderr=subprocess.STDOUT,
            )



if __name__ == '__main__':
    typer.run(main)


