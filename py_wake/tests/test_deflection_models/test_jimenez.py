from py_wake.deficit_models.gaussian import IEA37SimpleBastankhahGaussianDeficit
from py_wake.examples.data.hornsrev1 import V80
from py_wake.examples.data.iea37._iea37 import IEA37Site
from py_wake.deflection_models.jimenez import JimenezWakeDeflection
from py_wake.flow_map import YZGrid, XYGrid, XZGrid
import matplotlib.pyplot as plt
from py_wake import np
import pytest
from py_wake.tests import npt
from py_wake.wind_farm_models.engineering_models import PropagateDownwind
from py_wake.superposition_models import SquaredSum


@pytest.mark.parametrize('yaw,tilt,cx,cz', [
    (30, 0, -30, 70),
    (0, 30, 0, 100),
    (29.5805, 5, -30, 75)])
def test_yaw_tilt(yaw, tilt, cx, cz):
    site = IEA37Site(16)
    x, y = [0], [0]
    windTurbines = V80()

    D = windTurbines.diameter()
    wfm = PropagateDownwind(site, windTurbines, IEA37SimpleBastankhahGaussianDeficit(), superpositionModel=SquaredSum(),
                            deflectionModel=JimenezWakeDeflection())
    x_lst = np.linspace(-200, 1000, 100)
    y_lst = np.linspace(-100, 100, 201)
    z_lst = np.arange(10, 200, 1)

    fm_yz = wfm(x, y, wd=270, ws=10, yaw=yaw, tilt=tilt).flow_map(YZGrid(x=5 * D, y=y_lst, z=z_lst))
    fm_xz = wfm(x, y, wd=270, ws=10, yaw=yaw, tilt=tilt).flow_map(XZGrid(y=0, x=x_lst, z=z_lst))
    fm_xy = wfm(x, y, wd=270, ws=10, yaw=yaw, tilt=tilt).flow_map(XYGrid(x=x_lst))
    wake_center = fm_yz.WS_eff.where(fm_yz.WS_eff == fm_yz.WS_eff.min(), drop=True).squeeze()
    if 0:
        axes = plt.subplots(3, 1)[1].flatten()
        fm_xy.plot_wake_map(ax=axes[0])
        axes[0].axvline(5 * D)
        axes[0].plot(wake_center.x, wake_center.y, '.')
        fm_xz.plot_wake_map(ax=axes[1])
        axes[1].axvline(5 * D)
        axes[1].plot(wake_center.x, wake_center.h, '.')
        fm_yz.plot_wake_map(ax=axes[2])
        axes[2].plot(wake_center.y, wake_center.h, '.')
        plt.show()

    npt.assert_allclose(wake_center.y, cx, atol=.1)
    npt.assert_allclose(wake_center.h, cz, atol=.24)
