from __future__ import annotations
#from abc import abstractmethod
#from itertools import count
from typing import Optional, TYPE_CHECKING
import numpy as np

#from pyNastran.utils.numpy_utils import integer_types, cast_ints
#from pyNastran.bdf.field_writer_8 import print_card_8, set_blank_if_default
#from pyNastran.bdf.field_writer_16 import print_card_16 # , print_scientific_16, print_field_16
#from pyNastran.bdf.field_writer_double import print_scientific_double
from pyNastran.bdf.bdf_interface.assign_type import (
    integer, integer_or_blank, # integer_or_string,
    double_or_blank,
    string, string_or_blank, parse_components,
)
#from pyNastran.bdf.cards.elements.bars import set_blank_if_default

#from pyNastran.bdf.cards.base_card import expand_thru

from pyNastran.dev.bdf_vectorized3.cards.base_card import VectorizedBaseCard # , make_idim, hslice_by_idim
from pyNastran.dev.bdf_vectorized3.cards.write_utils import array_str, array_default_int, array_float, get_print_card_size
from pyNastran.dev.bdf_vectorized3.bdf_interface.geom_check import geom_check
from pyNastran.femutils.utils import hstack_lists


if TYPE_CHECKING:  # pragma: no cover
    from pyNastran.bdf.bdf_interface.bdf_card import BDFCard
    from pyNastran.nptyping_interface import NDArray3float
    from pyNastran.dev.bdf_vectorized3.bdf import BDF
    from pyNastran.dev.bdf_vectorized3.types import TextIOLike


class MONPNT1(VectorizedBaseCard):
    """
    +---------+---------+------+-----+-----+-------+------+----+----+
    |    1    |    2    |  3   |  4  |  5  |   6   |   7  | 8  | 9  |
    +=========+=========+======+=====+=====+=======+======+====+====+
    | MONPNT1 |  NAME   |                   LABEL                   |
    +---------+---------+------+-----+-----+-------+------+----+----+
    |         |  AXES   | COMP | CP  |  X  |   Y   |   Z  | CD |    |
    +---------+---------+------+-----+-----+-------+------+----+----+
    | MONPNT1 | WING155 |    Wing Integrated Load to Butline 155    |
    +---------+---------+------+-----+-----+-------+------+----+----+
    |         |    34   | WING |     | 0.0 | 155.0 | 15.0 |    |    |
    +---------+---------+------+-----+-----+-------+------+----+----+
    """
    _id_name = 'name'
    def __init__(self, model: BDF):
        super().__init__(model)
        self.name = np.array([], dtype='int32')

    #def __len__(self) -> int:
        #return len(self.name)

    def add(self, name: str, label: str, axes: str, aecomp_name: str,
            xyz: list[float],
            cp: int=0,
            cd: Optional[int]=None, comment: str='') -> MONPNT1:
        """
        Creates a MONPNT1 card

        Parameters
        ----------
        name : str
            Character string of up to 8 characters identifying the
            monitor point
        label : str
            A string comprising no more than 56 characters
            that identifies and labels the monitor point.
        axes : str
            components {1,2,3,4,5,6}
        aecomp_name : str
            name of the AECOMP/AECOMPL entry
        xyz : list[float, float, float]; default=None
            The coordinates in the CP coordinate system about which the
            loads are to be monitored.
            None : [0., 0., 0.]
        cp : int, CORDx; default=0
           int : coordinate system
        cd : int; default=None -> cp
            the coordinate system for load outputs
        comment : str; default=''
            a comment for the card

        Notes
        -----
        CD - MSC specific field

        """
        if cd is None:
            cd = -1
        self.cards.append((name, label, axes, aecomp_name, cp, xyz, cd, comment))
        self.n += 1

    def add_card(self, card: BDFCard, comment: str='') -> None:
        name = string(card, 1, 'name')
        label_fields = [labeli for labeli in card[2:8] if labeli is not None]
        label = ''.join(label_fields).strip()
        assert len(label) <= 56, label

        axes = parse_components(card, 9, 'axes')
        comp = string(card, 10, 'comp')
        cp = integer_or_blank(card, 11, 'cp', default=0)
        xyz = [
            double_or_blank(card, 12, 'x', default=0.0),
            double_or_blank(card, 13, 'y', default=0.0),
            double_or_blank(card, 14, 'z', default=0.0),
        ]
        cd = integer_or_blank(card, 15, 'cd', default=cp)
        self.cards.append((name, label, axes, comp, cp, xyz, cd, comment))
        self.n += 1

    def parse_cards(self):
        if self.n == 0:
            return
        ncards = len(self.cards)
        if ncards == 0:
            return
        name = np.zeros(ncards, dtype='|U8')
        label = np.zeros(ncards, dtype='|U72')
        comp = np.zeros(ncards, dtype='|U8')
        axes = np.zeros(ncards, dtype='int32')
        cp = np.zeros(ncards, dtype='int32')
        xyz = np.zeros((ncards, 3), dtype='float64')
        cd = np.zeros(ncards, dtype='int32')
        for icard, card in enumerate(self.cards):
            (namei, labeli, axesi, compi, cpi, xyzi, cdi, comment) = card
            name[icard] = namei
            label[icard] = labeli
            comp[icard] = compi
            axes[icard] = axesi
            cp[icard] = cpi
            xyz[icard, :] = xyzi
            cd[icard] = cdi
        self._save(name, label, comp, axes, cp, xyz, cd)
        self.sort()
        self.cards = []

    def _save(self, name, label, comp, axes, cp, xyz, cd):
        assert len(self.name) == 0, self.name
        self.name = name
        self.label = label
        self.comp = comp
        self.axes = axes
        self.cp = cp
        self.xyz = xyz
        self.cd = cd

    def __apply_slice__(self, monitor: MONPNT1, i: np.ndarray) -> None:  # ignore[override]
        monitor.n = len(i)
        monitor.name = self.name[i]
        monitor.label = self.label[i]
        monitor.comp = self.comp[i]
        monitor.axes = self.axes[i]
        monitor.cp = self.cp[i]
        monitor.xyz = self.xyz[i, :]
        monitor.cd = self.cd[i]

    def geom_check(self, missing: dict[str, np.ndarray]):
        #mids = hstack_msg([prop.material_id for prop in self.allowed_materials],
                          #msg=f'no materials for {self.type}')
        #mids.sort()
        coords = self.model.coord.coord_id
        #all_aecomp_names = self.model.aecomp.name
        #aecomp_names = np.unique(self.comp)
        ucoords = np.unique(np.hstack([self.cp, self.cd]))
        geom_check(self,
                   missing,
                   coord=(coords, ucoords),
                   #aecomp=(all_aecomp_names, aecomp_names),
                   )

    @property
    def max_id(self) -> int:
        return max(self.cp.max(), self.cd.max())

    def write_file(self, bdf_file: TextIOLike,
              size: int=8, is_double: bool=False,
              write_card_header: bool=False) -> None:
        if len(self.name) == 0:
            return None
        size = 8
        print_card, size = get_print_card_size(size, self.max_id)
        assert size == 8, size

        #cp = self.Cp()
        #cd = self.Cd()

        ## Default = the coordinate system specified by the CP field
        #if cd == cp:
            #cd = ''

        cps = array_default_int(self.cp, size=size)
        cds = array_str(self.cd, size=size)
        is_default_cd = (self.cp == self.cd)
        cds[is_default_cd] = ''
        #cds = array_default_int(self.cd, default=0, size=size)
        xyzs = array_float(self.xyz, size=size, is_double=False).tolist()
        for name, label, comp, axes, cp, xyz, cd in zip(self.name, self.label, self.comp, self.axes,
                                                        cps, xyzs, cds):
            x, y, z = xyz
            msg = 'MONPNT1 %-8s%s\n' % (name, label)
            msg += '        %-8s%-8s%-8s%-8s%-8s%-8s%-8s\n' % (
                axes, comp, cp, x, y, z,
                cd)
            bdf_file.write(msg)
        return


class MONPNT3(VectorizedBaseCard):
    """MSC Nastran specific card"""
    _id_name = 'name'

    def clear(self) -> None:
        self.name = np.array([], dtype='|U8')
        self.label = np.array([], dtype='|U72')
        self.axes = np.array([], dtype='int32')
        self.grid_set = np.array([], dtype='int32')
        self.elem_set = np.array([], dtype='int32')
        self.cp = np.array([], dtype='int32')
        self.xyz = np.zeros((0, 3), dtype='float64')
        self.cd = np.array([], dtype='int32')
        self.xflag = np.array([], dtype='|U1')

    #def __len__(self) -> int:
        #return len(self.name)

    def add(self, name: str, label: str, axes: str,
            grid_set: int, elem_set: int, xyz: list[float],
            cp: int=0, cd: Optional[int]=None,
            xflag='', comment: str='') -> MONPNT3:
        """Creates a MONPNT3 card"""
        if cd is None:
            # ew can do this because this is MSC-specific
            cd = cp
        self.cards.append((name, label, axes, grid_set, elem_set, xyz,
                           cp, cd, xflag, comment))
        self.n += 1

    def add_card(self, card: BDFCard, comment: str='') -> None:
        name = string(card, 1, 'name')

        label_fields = [labeli for labeli in card[2:8] if labeli is not None]
        label = ''.join(label_fields).strip()
        assert len(label) <= 56, label

        axes = parse_components(card, 9, 'axes')
        grid_set = integer(card, 10, 'grid_set')
        elem_set = integer_or_blank(card, 11, 'elem_set')
        cp = integer_or_blank(card, 12, 'cp', default=0)
        xyz = [
            double_or_blank(card, 13, 'x', default=0.0),
            double_or_blank(card, 14, 'y', default=0.0),
            double_or_blank(card, 15, 'z', default=0.0),
        ]
        xflag = string_or_blank(card, 16, 'xflag', default='')
        cd = integer_or_blank(card, 17, 'cd', default=cp)
        #return MONPNT3(name, label, axes, grid_set, elem_set, xyz,
                       #cp=cp, cd=cd, xflag=xflag, comment=comment)
        self.cards.append((name, label, axes, grid_set, elem_set, xyz,
                           cp, cd, xflag, comment))
        self.n += 1

    @VectorizedBaseCard.parse_cards_check
    def parse_cards(self):
        ncards = len(self.cards)
        name = np.zeros(ncards, dtype='|U8')
        label = np.zeros(ncards, dtype='|U72')
        axes = np.zeros(ncards, dtype='int32')
        grid_set = np.zeros(ncards, dtype='int32')
        elem_set = np.zeros(ncards, dtype='int32')
        cp = np.zeros(ncards, dtype='int32')
        xyz = np.zeros((ncards, 3), dtype='float64')
        cd = np.zeros(ncards, dtype='int32')
        xflag = np.zeros(ncards, dtype='|U1')
        for icard, card in enumerate(self.cards):
            (namei, labeli, axesi, grid_seti, elem_seti, xyzi,
             cpi, cdi, xflagi, comment) = card
            name[icard] = namei
            label[icard] = labeli
            axes[icard] = axesi
            grid_set[icard] = grid_seti
            elem_set[icard] = elem_seti
            cp[icard] = cpi
            xyz[icard, :] = xyzi
            cd[icard] = cdi
            xflag[icard] = xflagi
        self._save(name, label, axes, grid_set, elem_set, cp, xyz, cd, xflag)
        #self.sort()
        self.cards = []

    def _save(self, name, label, axes, grid_set, elem_set, cp, xyz, cd, xflag):
        assert len(self.name) == 0, self.name
        self.name = name
        self.label = label
        self.axes = axes
        self.grid_set = grid_set
        self.elem_set = elem_set
        self.cp = cp
        self.xyz = xyz
        self.cd = cd
        self.xflag = xflag

    def geom_check(self, missing: dict[str, np.ndarray]):
        #mids = hstack_msg([prop.material_id for prop in self.allowed_materials],
                          #msg=f'no materials for {self.type}')
        #mids.sort()
        coords = self.model.coord.coord_id
        #all_aecomp_names = self.model.aecomp.name
        #aecomp_names = np.unique(self.comp)
        ucoords = np.unique(np.hstack([self.cp, self.cd]))
        geom_check(self,
                   missing,
                   coord=(coords, ucoords),
                   #aecomp=(all_aecomp_names, aecomp_names),
                   )

    @property
    def max_id(self) -> int:
        return self.grid_set.max()

    def write_file(self, bdf_file: TextIOLike,
              size: int=8, is_double: bool=False,
              write_card_header: bool=False) -> None:
        if len(self.name) == 0:
            return None

        size = 8
        print_card, size = get_print_card_size(size, self.max_id)
        assert size == 8, size


        #cp = self.Cp()
        #cd = self.Cd()

        ## Default = the coordinate system specified by the CP field
        #if cd == cp:
            #cd = ''

        cps = array_default_int(self.cp, size=size)
        cds = array_str(self.cd, size=size)
        grid_sets = array_str(self.grid_set, size=size)
        elem_sets = array_str(self.elem_set, size=size)
        is_default_cd = (self.cp == self.cd)
        cds[is_default_cd] = ''
        #cds = array_default_int(self.cd, default=0, size=size)
        xyzs = array_float(self.xyz, size=size, is_double=False).tolist()
        for name, label, axes, grid_set, elem_set, \
            cp, xyz, xflag, cd in zip(self.name, self.label, self.axes,
                                      grid_sets, elem_sets,
                                      cps, xyzs, self.xflag, cds):
            x, y, z = xyz
            msg = (
                'MONPNT3 %-8s%s\n'
                '        %-8s%-8s%-8s%-8s%-8s%-8s%-8s%-8s\n'
                '        %-8s' % (
                    name, label,
                    axes, grid_set, elem_set, cp,
                    x, y, z, xflag,
                    cd))

            #msg = 'MONPNT3 %-8s%s\n' % (self.name, self.label)
            #msg += ('        %-8s%-8s%-8s%-8s%-8s%-8s%-8s%-8s\n'
                    #'         %-8s' % (
                        #self.axes, self.grid_set, self.elem_set, cp,
                        #print_float_8(x), print_float_8(y), print_float_8(z),
                        #xflag, cd
                    #))
            bdf_file.write(msg.rstrip('\n ') + '\n')
        return

#MONPNT2 = MONPNT1