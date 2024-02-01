from pydantic import BaseModel, validator, field_validator


class Tomography(BaseModel):
    iter_max: int
    lin_sys_LSQR_iter_max: int
    tomo_mat_damping_P: float
    tomo_mat_damping_P4V: float
    tomo_mat_damping_S: float
    tomo_mat_damping_S4V: float
    tomo_mat_damping_HP: float
    tomo_mat_damping_HP4V: float
    tomo_mat_damping_HS: float
    tomo_mat_damping_HS4V: float
    tomo_mat_damping_VP: float
    tomo_mat_damping_VP4V: float
    tomo_mat_damping_VS: float
    tomo_mat_damping_VS4V: float
    tomo_mat_srcs_psv_corr_H: float
    tomo_mat_srcs_psv_corr_I: float
    tomo_mat_srcs_psv_corr_V: float
    v_limits_p: list[float | int]
    v_limits_s: list[float | int]
    grid_size: list[float | int]
    base_model: list[list[int | float]]

    @field_validator('v_limits_p', 'v_limits_s')
    def v_limits_p_must_be_valid(cls, value):
        if len(value) != 2:
            raise ValueError('v_limits_p должен быть длиной 2')

        if value[0] > value[1]:
            raise ValueError('v_limits_p[0] должен быть меньше v_limits_p[1]')
        return value

    @field_validator('grid_size')
    def grid_size_must_be_valid(cls, value):
        if len(value) != 3:
            raise ValueError('grid_size должен быть длиной 3')
        return value

    class Config:
        from_attributes = True