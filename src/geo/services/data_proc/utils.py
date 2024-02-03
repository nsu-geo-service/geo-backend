from typing import Iterable

import numpy as np
import pandas as pd
from obspy import read_inventory, read_events
from obspy.core.event import Event

from geo.models.schemas import Phase


def rename_station(title: str) -> str:
    names = {
        "SML04": "1",
        "SML02": "2",
        "SML05": "3",
        "SML06": "4",
        "SML07": "5",
        "SML15": "6",
        "SML16": "7",
        "SML00": "8",
        "SML17": "9",
        "SML18": "10",
        "SML01": "11",
        "SML03": "12",
        "SML08": "13",
        "SML09": "14",
        "SML10": "15",
        "SML11": "16",
        "SML12": "17",
        "SML13": "18",
        "SML14": "19",
    }
    return names.get(title, title)


def stations(filepath: str) -> dict[str, list]:
    inventory = read_inventory(filepath)

    data = {
        'station': [],
        'network': [],
        'x': [],
        'y': [],
        'z': []
    }

    for network in inventory:
        for station in network:
            data['station'].append(rename_station(station.code))
            data['network'].append(network.code)
            data['y'].append(station.latitude)
            data['x'].append(station.longitude)
            data['z'].append(station.elevation / 1000)

    df = pd.DataFrame(data)
    df['station'] = df['station'].astype(int)
    df.sort_values(by='station', inplace=True)

    return df.to_dict(orient='list')


def quake(filepath: str) -> tuple[
    dict[str, tuple[str, str, float, float, float]],
    dict[int, tuple[list[tuple[Phase, float]], str]]
]:
    events = {}
    detections = {}

    events_data: Iterable[Event] = read_events(filepath)
    for index, event in enumerate(events_data):
        if len(event.picks) % 3 != 0:
            raise ValueError("Длина не делится на 3 без остатка. Ошибка.")
        elif len(event.origins) == 1:
            prev_station = []
            I = []
            for i in range(len(event.picks)):
                if event.picks[i].waveform_id.channel_code == 'HHN':
                    time_origin = event.origins[0].time

                    if not prev_station:
                        prev_station.append(event.picks[i].waveform_id.station_code)
                        I.append(i)

                    else:
                        current_station = event.picks[i].waveform_id.station_code
                        search_station_equal = np.where(np.array(prev_station) == current_station)[0]
                        if len(search_station_equal) > 0:
                            INDEX = search_station_equal[0]

                            event_name = index
                            network = event.picks[I[INDEX]].waveform_id.network_code
                            x = event.origins[0].longitude
                            y = event.origins[0].latitude
                            z = event.origins[0].depth
                            magnitude = event.magnitudes[0].mag

                            events[event_name] = (time_origin, magnitude, network, x, y, z)

                            phase = Phase.P if event.picks[I[INDEX]].phase_hint == "P" else Phase.S
                            time = np.round(np.abs(time_origin - event.picks[I[INDEX]].time), 4)

                            if event_name not in detections:
                                detections[event_name] = ([(phase, time)], rename_station(current_station))
                            else:
                                detections[event_name][0].append((phase, time))

                            # Add data for the current pick
                            phase = Phase.P if event.picks[i].phase_hint == "P" else Phase.S
                            time = np.round(np.abs(time_origin - event.picks[i].time), 4)

                            detections[event_name][0].append((phase, time))

                            prev_station.append(event.picks[i].waveform_id.station_code)
                            I.append(i)

                        else:
                            prev_station.append(event.picks[i].waveform_id.station_code)
                            I.append(i)

    return events, detections


"""

```
def quake(filepath: str):
    data = {
        'Network': [],
        'Station': [],
        'Phase': [],
        'Time': [],
        'Event': [],
        'x': [],
        'y': [],
        'z': []
    }

    events: Iterable[Event] = read_events(filepath)
    for index, event in enumerate(events):
        if len(event.picks) % 3 != 0:
            raise ValueError("Длина не делится на 3 без остатка. Ошибка.")
        else:
            prev_station = []
            I = []
            for i in range(len(event.picks)):
                if event.picks[i].waveform_id.channel_code == 'HHN':
                    time_origin = event.origins[0].time

                    if not prev_station:
                        prev_station.append(event.picks[i].waveform_id.station_code)
                        I.append(i)

                    else:
                        current_station = event.picks[i].waveform_id.station_code
                        search_station_equal = np.where(np.array(prev_station) == current_station)[0]
                        if len(search_station_equal) > 0:
                            INDEX = search_station_equal[0]

                            data['Network'].append(event.picks[I[INDEX]].waveform_id.network_code)
                            data['Station'].append(event.picks[I[INDEX]].waveform_id.station_code)
                            data['Phase'].append(event.picks[I[INDEX]].phase_hint)
                            data['Time'].append(np.round(np.abs(time_origin - event.picks[I[INDEX]].time), 4))
                            data['Event'].append(index)
                            data['x'].append(event.origins[0].longitude)
                            data['y'].append(event.origins[0].latitude)
                            data['z'].append(event.origins[0].depth)

                            data['Network'].append(event.picks[i].waveform_id.network_code)
                            data['Station'].append(event.picks[i].waveform_id.station_code)
                            data['Phase'].append(event.picks[i].phase_hint)
                            data['Time'].append(np.round(np.abs(time_origin - event.picks[i].time), 4))
                            data['Event'].append(index)
                            data['x'].append(event.origins[0].longitude)
                            data['y'].append(event.origins[0].latitude)
                            data['z'].append(event.origins[0].depth)
                            prev_station.append(event.picks[i].waveform_id.station_code)
                            I.append(i)

                        else:
                            prev_station.append(event.picks[i].waveform_id.station_code)
                            I.append(i)
    return data
```
Перепиши так, 
чтобы я получал что-то типа:  events = { "event_name": (network, x, y, z), ... }  detections = { "event_name": [ (Phase, time), ... ], ... }
При
"""
