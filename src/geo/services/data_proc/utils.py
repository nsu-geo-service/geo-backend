from typing import Iterator, Iterable

import numpy as np
import obspy
import pandas as pd
from obspy import read_inventory, read_events, Catalog
from obspy.core.event import Event
from scipy.ndimage import zoom

from geo.models.schemas import Phase


def change_station_on_number(dataframe):
    dataframe['Station'] = dataframe['Station'].str.replace('SML04', '1')
    dataframe['Station'] = dataframe['Station'].str.replace('SML02', '2')
    dataframe['Station'] = dataframe['Station'].str.replace('SML05', '3')
    dataframe['Station'] = dataframe['Station'].str.replace('SML06', '4')

    dataframe['Station'] = dataframe['Station'].str.replace('SML07', '5')
    dataframe['Station'] = dataframe['Station'].str.replace('SML15', '6')
    dataframe['Station'] = dataframe['Station'].str.replace('SML16', '7')
    dataframe['Station'] = dataframe['Station'].str.replace('SML00', '8')

    dataframe['Station'] = dataframe['Station'].str.replace('SML17', '9')
    dataframe['Station'] = dataframe['Station'].str.replace('SML18', '10')
    dataframe['Station'] = dataframe['Station'].str.replace('SML01', '11')
    dataframe['Station'] = dataframe['Station'].str.replace('SML03', '12')

    dataframe['Station'] = dataframe['Station'].str.replace('SML08', '13')
    dataframe['Station'] = dataframe['Station'].str.replace('SML09', '14')
    dataframe['Station'] = dataframe['Station'].str.replace('SML10', '15')
    dataframe['Station'] = dataframe['Station'].str.replace('SML11', '16')

    dataframe['Station'] = dataframe['Station'].str.replace('SML12', '17')
    dataframe['Station'] = dataframe['Station'].str.replace('SML13', '18')
    dataframe['Station'] = dataframe['Station'].str.replace('SML14', '19')

    return dataframe


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


def relief_reader(path_relief, grid_size):
    relief = pd.read_csv(path_relief, sep=r"\s+", names=['y', 'x', 'z'])
    relief = relief.sort_values(['y', 'x'])

    x_array = np.array(relief['x'])
    y_array = np.array(relief['y'])

    x_coords = list(set(x_array))
    y_coords = list(set(y_array))

    x_max = np.max(x_coords)
    x_min = np.min(x_coords)
    y_max = np.max(y_coords)
    y_min = np.min(y_coords)

    x_middle = x_min + np.abs(x_min - x_max) / 2
    y_middle = y_min + np.abs(y_min - y_max) / 2

    z_coords = np.asarray(relief['z']).reshape(len(x_coords), len(y_coords)) / 1000

    depth_topography = zoom(z_coords,
                            (grid_size[0] / z_coords.shape[0],
                             grid_size[1] / z_coords.shape[1]),
                            order=0)

    x_mi, y_mi, z_mi = change_coords_to_ST3D(np.asarray(x_min), np.asarray(y_min), np.asarray(np.min(z_coords)),
                                             x_middle, y_middle)
    x_ma, y_ma, z_ma = change_coords_to_ST3D(np.asarray(x_max), np.asarray(y_max), np.asarray(np.max(z_coords)),
                                             x_middle, y_middle)
    X_Y_Z = np.asarray((x_ma, y_mi, z_mi, x_mi, y_ma, z_ma))

    return x_middle, y_middle, depth_topography, X_Y_Z


def create_start_model(start_model_path, grid_size):
    start_model = pd.read_csv(start_model_path, sep=r"\s+", names=['Z', 'Vp', 'Vs'])
    start_model.drop(index=start_model.index[0], axis=0, inplace=True)

    Vp_st = np.asarray(pd.to_numeric(start_model['Vp'])).reshape(len(start_model), 1, 1)
    Vs_st = np.asarray(pd.to_numeric(start_model['Vs'])).reshape(len(start_model), 1, 1)

    Vp_st = zoom(Vp_st, (grid_size[0] / Vp_st.shape[0],
                         grid_size[1] / Vp_st.shape[1],
                         grid_size[2] / Vp_st.shape[2]),
                 order=0)
    Vs_st = zoom(Vs_st, (grid_size[0] / Vs_st.shape[0],
                         grid_size[1] / Vs_st.shape[1],
                         grid_size[2] / Vs_st.shape[2]),
                 order=0)

    return Vp_st, Vs_st


def get_network_codes():
    path = 'http://84.237.52.214:8080/fdsnws/station/1/query?'
    inventory = read_inventory(path)
    codes = []
    for network in inventory:
        codes.append(network.code)

    return codes


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

    return data


def quake(filepath: str) -> tuple[
    dict[str, tuple[str, float, float, float]],
    dict[str, tuple[list[tuple[str, float]], str]]
]:
    events = {}
    detections = {}

    events_data: Iterable[Event] = read_events(filepath)
    for index, event in enumerate(events_data):
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

                            event_name = index
                            network = event.picks[I[INDEX]].waveform_id.network_code
                            x = event.origins[0].longitude
                            y = event.origins[0].latitude
                            z = event.origins[0].depth

                            events[event_name] = (network, x, y, z)

                            phase = Phase.P if event.picks[I[INDEX]].phase_hint else Phase.S
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
