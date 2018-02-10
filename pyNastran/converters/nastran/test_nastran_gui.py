"""tests the NastranIO class"""
import os
import unittest
from pyNastran.gui.testing_methods import FakeGUIMethods
from pyNastran.converters.nastran.nastran_io import NastranIO
import pyNastran
#from pyNastran.utils.log import get_logger2

class NastranGUI(NastranIO, FakeGUIMethods):
    def __init__(self, inputs=None):
        FakeGUIMethods.__init__(self, inputs=inputs)
        NastranIO.__init__(self)

PKG_PATH = pyNastran.__path__[0]
MODEL_PATH = os.path.join(PKG_PATH, '..', 'models')


class TestNastranGUI(unittest.TestCase):

    def test_solid_shell_bar_01(self):
        bdf_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'static_solid_shell_bar.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'static_solid_shell_bar.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_solid_shell_bar_02(self):
        bdf_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'mode_solid_shell_bar.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'mode_solid_shell_bar.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_solid_shell_bar_03(self):
        bdf_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'buckling_solid_shell_bar.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'sol_101_elements', 'buckling_solid_shell_bar.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_solid_bending(self):
        bdf_filename = os.path.join(MODEL_PATH, 'solid_bending', 'solid_bending.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'solid_bending', 'solid_bending.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_beam_modes_01(self):
        """CBAR/CBEAM - PARAM,POST,-1"""
        bdf_filename = os.path.join(MODEL_PATH, 'beam_modes', 'beam_modes.dat')
        op2_filename = os.path.join(MODEL_PATH, 'beam_modes', 'beam_modes_m1.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_beam_modes_02(self):
        """CBAR/CBEAM - PARAM,POST,-2"""
        bdf_filename = os.path.join(MODEL_PATH, 'beam_modes', 'beam_modes.dat')
        op2_filename = os.path.join(MODEL_PATH, 'beam_modes', 'beam_modes_m2.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_beam_modes_03(self):
        dirname = os.path.join(MODEL_PATH, 'beam_modes')
        bdf_filename = os.path.join(dirname, 'beam_modes.dat')
        op2_filename = os.path.join(dirname, 'beam_modes_m1.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        #test.load_nastran_results(op2_filename)

        test.load_nastran_geometry(bdf_filename)
        #test.load_nastran_results(op2_filename)

        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_beam_modes_04(self):
        dirname = os.path.join(MODEL_PATH, 'beam_modes')
        bdf_filename = os.path.join(dirname, 'beam_modes.dat')
        op2_filename = os.path.join(dirname, 'beam_modes_m2.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

        test.load_nastran_geometry(bdf_filename)


    #@unittest.expectedFailure
    #def test_contact(self):
        #"""this test fails because of a misparsed card"""
        #bdf_filename = os.path.join(MODEL_PATH, 'contact', 'contact.bdf')
        #op2_filename = os.path.join(MODEL_PATH, 'contact', 'contact.op2')

        #test = NastranGUI()
        #test.load_nastran_geometry(bdf_filename)
        #test.load_nastran_results(op2_filename)

    def test_fsi(self):
        """tests -1 coordinate systems (flag for a fluid contact face)"""
        bdf_filename = os.path.join(MODEL_PATH, 'fsi', 'fsi.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'fsi', 'fsi.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_thermal_01(self):
        dirname = os.path.join(MODEL_PATH, 'thermal')
        bdf_filename = os.path.join(dirname, 'thermal_test_153.bdf')
        op2_filename = os.path.join(dirname, 'thermal_test_153.op2')

        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_bwb_gui(self):
        bdf_filename = os.path.join(MODEL_PATH, 'bwb', 'BWB_saero.bdf')
        test = NastranGUI()
        #test.log = get_logger2()
        test.load_nastran_geometry(bdf_filename)

    def test_femap_rougv1_01(self):
        """tests the exhaust manifold and it's funny eigenvectors"""
        dirname = os.path.join(MODEL_PATH, 'femap_exhaust')
        #bdf_filename = os.path.join(dirname, 'modal_example.bdf')
        op2_filename = os.path.join(dirname, 'modal_example.op2')

        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_aero(self):
        """tests the bah_plane"""
        bdf_filename = os.path.join(MODEL_PATH, 'aero', 'bah_plane', 'bah_plane.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'aero', 'bah_plane', 'bah_plane.op2')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_01(self):
        """tests forces/pressure in SOL 101"""
        bdf_filename = os.path.join(MODEL_PATH, 'elements', 'static_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'static_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)
        test.on_fringe(icase=43)
        test.on_vector(icase=43)# force_xyz
        test.on_disp(icase=45)# disp
        test.on_clear_results()

        test.on_fringe(icase=43)
        test.on_vector(icase=43)# force_xyz
        test.on_disp(icase=45)# disp

    def test_gui_elements_02(self):
        """tests a large number of elements and results in SOL 101"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'static_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'static_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_03(self):
        """tests a large number of elements and results in SOL 103-modes"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'modes_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'modes_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_04(self):
        """tests a large number of elements and results in SOL 108-freq"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'freq_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'freq_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_05(self):
        """tests a large number of elements and results in SOL 108-freq"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'freq_elements2.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'freq_elements2.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_06(self):
        """tests a large number of elements and results in SOL 106-loadstep"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'loadstep_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'loadstep_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_07(self):
        """tests a large number of elements and results in SOL 107-complex modes"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'modes_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'modes_complex_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_elements_08(self):
        """tests a large number of elements and results in SOL 109-linear time"""
        bdf_filename = os.path.join(MODEL_PATH, 'elements', 'modes_elements.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'elements', 'time_elements.op2')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_pload_01(self):
        """tests a PLOAD4/CTETRA"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'ctetra.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'pload4', 'ctetra.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_pload_02(self):
        """tests a PLOAD4/CHEXA"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'chexa.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'pload4', 'chexa.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_pload_03(self):
        """tests a PLOAD4/CPENTA"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'cpenta.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'pload4', 'cpenta.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_pload_04(self):
        """tests a PLOAD4/CQUAD4"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'cquad4.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'pload4', 'cquad4.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_pload_05(self):
        """tests a PLOAD4/CTRIA3"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'ctria3.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'pload4', 'ctria3.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    #def test_gui_pload_06(self):
        #"""tests a PLOAD1/CBAR"""
        #bdf_filename = os.path.join(MODEL_PATH, 'elements', 'pload1.bdf')
        #op2_filename = os.path.join(MODEL_PATH, 'pload4', 'pload1.op2')
        #test = NastranGUI()
        #test.load_nastran_geometry(op2_filename)
        #test.load_nastran_results(op2_filename)

    def test_gui_bar_bar(self):
        """tests a PBARL/BAR"""
        bdf_filename = os.path.join(MODEL_PATH, 'bars', 'pbarl_bar.bdf')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)

    def test_gui_bar_box(self):
        """tests a PBARL/BOX"""
        bdf_filename = os.path.join(MODEL_PATH, 'bars', 'pbarl_bar.bdf')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)

    def test_gui_bar_t(self):
        """tests a PBARL/T"""
        bdf_filename = os.path.join(MODEL_PATH, 'bars', 'pbarl_t.bdf')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)

    def test_gui_bar_t2(self):
        """tests a PBARL/T2"""
        bdf_filename = os.path.join(MODEL_PATH, 'bars', 'pbarl_t2.bdf')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)

    def test_gui_bar_i(self):
        """tests a PBARL/I"""
        bdf_filename = os.path.join(MODEL_PATH, 'bars', 'pbarl_i.bdf')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)

    def test_gui_thermal_01(self):
        """tests thermal"""
        #bdf_filename = os.path.join(MODEL_PATH, 'thermal', 'thermal_test_153.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'thermal', 'thermal_test_153.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_thermal_02(self):
        """tests thermal"""
        #bdf_filename = os.path.join(MODEL_PATH, 'thermal', 'hd15901.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'thermal', 'hd15901.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_thermal_03(self):
        """tests thermal"""
        #bdf_filename = os.path.join(MODEL_PATH, 'other', 'hd15306.bdf')
        op2_filename = os.path.join(MODEL_PATH, 'other', 'hd15306.op2')
        test = NastranGUI()
        test.load_nastran_geometry(op2_filename)
        test.load_nastran_results(op2_filename)

    def test_gui_dvprel(self):
        """tests dvprel"""
        bdf_filename = os.path.join(MODEL_PATH, 'other', 'dofm12.bdf')
        #op2_filename = os.path.join(MODEL_PATH, 'other', 'dofm12.op2')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        #test.load_nastran_results(op2_filename)

    def test_gui_patran(self):
        """tests patran format"""
        bdf_filename = os.path.join(MODEL_PATH, 'patran_fmt', '0012_20.bdf')
        nod_filename = os.path.join(MODEL_PATH, 'patran_fmt', 'normals.nod')
        test = NastranGUI()
        test.load_nastran_geometry(bdf_filename)
        test.load_nastran_results(nod_filename)

#def test_bottle():  # pragma: no cover
    #"""
    #Tests Nastran GUI loading
    #"""
    #test = NastranGUI()
    #test.load_nastran_geometry('bottle_shell_w_holes_pmc.bdf', '')
    #test.load_nastran_results('bottle_shell_w_holes_pmc.op2', '')

    #keys = test.result_cases.keys()
    #assert (1, 'Stress1', 1, 'centroid', '%.3f') in keys, keys

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
