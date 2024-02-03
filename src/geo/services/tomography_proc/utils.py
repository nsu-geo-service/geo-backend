import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter, zoom
import h5py
from matplotlib.colors import ListedColormap
import pyvista as pv


def relief_read(path_relief, grid_size):
    relief = pd.read_csv(path_relief, sep=r"\s+", names=['y', 'x', 'z'])

    # Todo: значения по умолчанию или введенные пользователем
    relief = relief.drop(relief[relief.y > 128].index)
    relief = relief.drop(relief[relief.y < 125].index)
    relief = relief.drop(relief[relief.x > 73.5].index)
    relief = relief.drop(relief[relief.x < 71.1].index)

    relief = relief.sort_values(['y', 'x'])

    x_array = np.array(relief['x'])
    y_array = np.array(relief['y'])

    x_coords = list(set(x_array))
    y_coords = list(set(y_array))

    x_max = np.max(x_coords)
    x_min = np.min(x_coords)
    y_max = np.max(y_coords)
    y_min = np.min(y_coords)
    print(x_min, x_max, y_min, y_max)

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

    return x_middle, y_middle, -depth_topography, X_Y_Z


def create_start_model(data: list[list[float]], grid_size):
    start_model = pd.DataFrame(data, columns=['Z', 'Vp', 'Vs'])
    start_model.drop(index=start_model.index[0], axis=0, inplace=True)

    Vp_st = np.asarray(pd.to_numeric(start_model['Vp'])).reshape(1, 1, len(start_model))
    Vs_st = np.asarray(pd.to_numeric(start_model['Vs'])).reshape(1, 1, len(start_model))

    Vp_st = zoom(
        Vp_st,
        (
            grid_size[0] / Vp_st.shape[0],
            grid_size[1] / Vp_st.shape[1],
            grid_size[2] / Vp_st.shape[2]
        ),
        order=0
    )
    Vs_st = zoom(
        Vs_st,
        (
            grid_size[0] / Vs_st.shape[0],
            grid_size[1] / Vs_st.shape[1],
            grid_size[2] / Vs_st.shape[2]
        ),
        order=0
    )
    Vp_st = gaussian_filter(Vp_st, sigma=2)
    Vs_st = gaussian_filter(Vs_st, sigma=2)

    return Vp_st, Vs_st


def change_coords_to_ST3D(FI, TET, h, fi0, tet0):
    PI = 3.1415926
    Rz = 6371.0
    PER = PI / 180.0
    TET1 = TET * PER
    R = Rz - h

    Y1 = R * np.cos((FI - fi0) * PER) * np.cos(TET1)
    X = R * np.sin((FI - fi0) * PER) * np.cos(TET1)
    Z1 = R * np.sin(TET1)

    T = tet0 * PER

    Y = -Y1 * np.sin(T) + Z1 * np.cos(T)
    Z = Rz - (Y1 * np.cos(T) + Z1 * np.sin(T))

    return X, Y, Z


def to_vtk(input_file_path, output_file_path, filepath, grid_size, X_Y_Z_rcvrs, X_Y_Z_srcs, Grid_Step, LIM_COORD):
    h_5_file_in_ = []
    h_5_file_out_ = []
    f_in_ = h5py.File(input_file_path, 'r')
    f_out_ = h5py.File(output_file_path, 'r')
    VP_0 = f_in_['HPS_ST3D']['Input']['VGrid']['VS'][:, :, :]
    VP_1 = f_out_['HPS_ST3D']['Iter_2']['VGrid']['VS'][:, :, :]
    dVp = (VP_1 / VP_0 - 1) * 100

    grid = pv.ImageData()
    grid.dimensions = np.array(dVp.shape)
    grid.origin = LIM_COORD
    grid.spacing = np.array(
        [
            (Grid_Step[0]) / (grid_size[0] - 1),
            (Grid_Step[1]) / (grid_size[1] - 1),
            (Grid_Step[2]) / (grid_size[2] - 1)
        ],
        dtype=np.float64
    )

    grid.point_data['V'] = dVp.flatten(order="F")

    # код для станций и сфер
    radius_cone = 3  # радиус конуса
    radius_spheres = 0.9
    height_cone = 3  # Высота конусов
    numb_face = 3  # Кол-во граней конуса
    coefficient_z_geom = 1  # Коэффициент для z координаты расположения фигур
    direction = (0, 0, -1)  # направление вершины конуса
    cones = pv.MultiBlock([pv.Cone(center=X_Y_Z_rcvrs[k],
                                   direction=direction,
                                   radius=radius_cone,
                                   height=height_cone,
                                   resolution=numb_face) for k in range(len(X_Y_Z_rcvrs))])
    spheres = pv.MultiBlock([pv.Sphere(radius=1 / radius_spheres,
                                       center=X_Y_Z_srcs[i]) for i in range(len(X_Y_Z_srcs))])

    # палетка

    Down = np.array([116 / 255, 38 / 255, 38 / 255, 1])
    color1 = np.array([129 / 255, 24 / 255, 24 / 255, 1])
    color2 = np.array([159 / 255, 0, 0, 1])
    color3 = np.array([208 / 255, 0, 0, 1])
    color4 = np.array([1, 3 / 255, 0, 1])
    color5 = np.array([1, 64 / 255, 0, 1])
    color6 = np.array([1, 117 / 255, 0, 1])
    color7 = np.array([1, 157 / 255, 0, 1])
    color8 = np.array([1, 196 / 255, 0, 1])
    color9 = np.array([1, 235 / 255, 158 / 255, 1])
    color10 = np.array([232 / 255, 255 / 255, 255 / 255, 1])
    color11 = np.array([222 / 252, 1, 1, 1])
    color12 = np.array([156 / 255, 1, 1, 1])
    color13 = np.array([60 / 255, 1, 1, 1])
    color14 = np.array([25 / 255, 192 / 255, 1, 1])
    color15 = np.array([89 / 258, 160 / 255, 1, 1])
    color16 = np.array([119 / 255, 136 / 255, 238 / 255, 1])
    color17 = np.array([141 / 255, 114 / 255, 216 / 255, 1])
    color18 = np.array([141 / 255, 77 / 255, 204 / 255, 1])
    Up = np.array([112 / 255, 19 / 255, 204 / 255, 1])

    mapping = np.linspace(-10, 10, 255)

    newcolors = np.empty((255, 4))
    newcolors[mapping >= 9] = Up
    newcolors[mapping < 9] = color18
    newcolors[mapping < 8] = color17
    newcolors[mapping < 7] = color16
    newcolors[mapping < 6] = color15
    newcolors[mapping < 5] = color14
    newcolors[mapping < 4] = color13
    newcolors[mapping < 3] = color12
    newcolors[mapping < 2] = color11
    newcolors[mapping < 1] = color10
    newcolors[mapping < 0] = color9
    newcolors[mapping < -1] = color8
    newcolors[mapping < -2] = color7
    newcolors[mapping < -3] = color6
    newcolors[mapping < -4] = color5
    newcolors[mapping < -5] = color4
    newcolors[mapping < -6] = color3
    newcolors[mapping < -7] = color2
    newcolors[mapping < -8] = color1
    newcolors[mapping < -9] = Down
    my_colormap = ListedColormap(newcolors)

    # отрисовка

    # mesh = grid.slice_orthogonal(x = 5)
    # mesh.plot(show_edges=True, notebook=False,lighting='three lights', show_bounds = True)
    p = pv.Plotter(notebook=False, lighting='three lights')

    p.add_mesh_slice(grid, assign_to_axis='x', cmap=my_colormap, clim=[-10, 10], interpolate_before_map=True)
    p.add_mesh_slice(grid, assign_to_axis='y', cmap=my_colormap, clim=[-10, 10], interpolate_before_map=True)
    p.add_mesh_slice(grid, assign_to_axis='z', cmap=my_colormap, clim=[-10, 10], interpolate_before_map=True)
    # p.add_mesh(cones, color='blue')
    # p.add_mesh(spheres, cmap='Reds')
    p.show_bounds()

    mesh = pv.PolyData()
    obj = mesh.merge(grid)
    obj.save(filepath)
