import warnings
from struct import Struct, pack
from typing import List, Tuple

import numpy as np
from numpy import zeros

from pyNastran.utils.numpy_utils import integer_types
from pyNastran.op2.result_objects.op2_objects import get_complex_times_dtype
from pyNastran.op2.tables.oes_stressStrain.real.oes_objects import StressObject, StrainObject, OES_Object
from pyNastran.f06.f06_formatting import write_imag_floats_13e, write_float_13e

#BASIC_TABLES = {
    #'OES1X', 'OES1',
    #'OES2',
    #'OSTR1X',
#}
#VM_TABLES = {'OESVM1', 'OESVM2',
             #'OSTRVM1', 'OSTRVM2'}


class ComplexPlateVMArray(OES_Object):
    r"""
       ELEMENT      FIBER                                     - STRESSES IN ELEMENT  COORDINATE SYSTEM -
          ID.       DISTANCE              NORMAL-X                       NORMAL-Y                      SHEAR-XY               VON MISES
    0     101  -5.000000E-01  -8.152692E-01 /  0.0           -1.321875E+00 /  0.0           -3.158517E+00 /  0.0            5.591334E+00
                5.000000E-01   1.728573E+00 /  0.0           -7.103837E+00 /  0.0            2.856040E+00 /  0.0            9.497519E+00

    floats = (1011,
              -0.5, -0.8152692, 0.0, -1.321874, 0.0, -3.158516, 0.0, 5.591334,
               0.5,  1.7285730, 0.0, -7.103837, 0.0,  2.856039, 0.0, 9.497518)
    """
    def __init__(self, data_code, is_sort1, isubcase, dt):
        OES_Object.__init__(self, data_code, isubcase, apply_data_code=False)   ## why???
        self.element_node = None
        #self.code = [self.format_code, self.sort_code, self.s_code]

        #self.ntimes = 0  # or frequency/mode
        #self.ntotal = 0
        #self.itime = 0
        self.nelements = 0  # result specific

        #if is_sort1:
            #pass
        #else:
            #raise NotImplementedError('SORT2')

    @property
    def is_real(self) -> bool:
        return False

    @property
    def is_complex(self) -> bool:
        return True

    def _reset_indices(self) -> None:
        self.itotal = 0
        self.ielement = 0

    @property
    def nnodes_per_element(self) -> int:
        return get_nnodes(self)

    #@property
    #def nnodes(self):
        #return self.nnodes_per_element()

    def build(self) -> None:
        """sizes the vectorized attributes of the ComplexPlateArray

        SORT1:
         - etype   SORT ndata numwide size  -> nelements     ntimes                 nnodes ntotal_layers
         - CQUAD8  1    1044  87      4        1044/(4*87)=3 xxx                    5      3*5=15        C:\MSC.Software\simcenter_nastran_2019.2\tpl_post2\tr1081x.op2
         - QUADR   2    3828  87               1             3828/(4*87)=11         10     2*1*10=20     C:\MSC.Software\simcenter_nastran_2019.2\tpl_post2\cqromids111.op2

        """
        if not hasattr(self, 'subtitle'):
            self.subtitle = self.data_code['subtitle']
        nnodes = self.nnodes_per_element
        #print(self._ntotals, self.ntotal)
        #print(self.code_information())

        #self.names = []
        #self.nelements //= nnodes
        self.nelements //= self.ntimes
        #print('element_type=%r ntimes=%s nelements=%s nnodes=%s ntotal=%s subtitle=%s' % (
            #self.element_type, self.ntimes, self.nelements, nnodes, self.ntotal, self.subtitle))

        #self.ntotal = self.nelements * nnodes * 2
        #self.ntotal
        self.itime = 0
        self.ielement = 0
        self.itotal = 0
        #print('ntotal=%s ntimes=%s nelements=%s' % (self.ntotal, self.ntimes, self.nelements))

        #print("ntimes=%s nelements=%s ntotal=%s" % (self.ntimes, self.nelements, self.ntotal))
        dtype, idtype, cfdtype = get_complex_times_dtype(self.nonlinear_factor, self.size)

        # nelements is the actual number of elements
        if self.is_sort1:
            ntimes = self.ntimes
            nelements = self.ntotal // 2
            nlayers = self.ntotal
            #print(f'  SORT1: ntimes={ntimes} nelements={nelements} nlayers={nlayers} {self.element_name}-{self.element_type}')
        elif self.is_sort2:
            #print(self._ntotals)
            nelements = self.ntimes
            nlayers = nelements * 2 * nnodes
            ntimes = self.ntotal // (2 * nnodes)
            #print(f'  SORT2: ntimes={ntimes} nelements={nelements} nnodes={nnodes} nlayers={nlayers} {self.element_name}-{self.element_type}')
        #print(f'{self.element_name}-{self.element_type} nelements={nelements} nlayers={nlayers} ntimes={ntimes}')

        self._times = zeros(ntimes, dtype=dtype)
        #self.ntotal = self.nelements * nnodes

        # the number is messed up because of the offset for the element's properties

        #if not self.nelements * nnodes * 2 == self.ntotal:
            #msg = 'ntimes=%s nelements=%s nnodes=%s ne*nn=%s ntotal=%s' % (
                #self.ntimes, self.nelements, nnodes,
                #self.nelements * nnodes, self.ntotal)
            #raise RuntimeError(msg)

        self.fiber_distance = zeros(nlayers, 'float32')

        # [oxx, oyy, txy, ovm]
        self.data = zeros((ntimes, nlayers, 4), dtype=cfdtype)

        # we could use nelements*2 to make it smaller, but it'd be harder
        self.element_node = zeros((nlayers, 2), dtype=idtype)

        # TODO: could be more efficient by using nelements for cid
        #self.element_cid = zeros((self.nelements, 2), 'int32')
        #print(self.data.shape, self.element_node.shape)

    def build_dataframe(self) -> None:
        """creates a pandas dataframe"""
        headers = self.get_headers()
        column_names, column_values = self._build_dataframe_transient_header()

        data_frame = self._build_pandas_transient_element_node(
            column_values, column_names,
            headers, self.element_node, self.data)
        #print(data_frame)
        self.data_frame = data_frame

    def __eq__(self, table):  # pragma: no cover
        assert self.is_sort1 == table.is_sort1
        self._eq_header(table)
        if not np.array_equal(self.data, table.data):
            msg = 'table_name=%r class_name=%s\n' % (self.table_name, self.__class__.__name__)
            msg += '%s\n' % str(self.code_information())
            ntimes = self.data.shape[0]

            i = 0
            if self.is_sort1:
                for itime in range(ntimes):
                    for ieid, (eid, nid) in enumerate(self.element_node):
                        t1 = self.data[itime, ieid, :]
                        t2 = table.data[itime, ieid, :]
                        (oxx1, oyy1, txy1) = t1
                        (oxx2, oyy2, txy2) = t2
                        #d = t1 - t2
                        if not np.allclose(
                                [oxx1.real, oxx1.imag, oyy1.real, oyy1.imag, txy1.real, txy1.imag, ], # atol=0.0001
                                [oxx2.real, oxx2.imag, oyy2.real, oyy2.imag, txy2.real, txy2.imag, ], atol=0.075):
                            ni = len(str(eid)) + len(str(nid))
                        #if not np.array_equal(t1, t2):
                            msg += ('(%s %s)  (%s, %sj, %s, %sj, %s, %sj)\n'
                                    '%s     (%s, %sj, %s, %sj, %s, %sj)\n' % (
                                        eid, nid,
                                        oxx1.real, oxx1.imag, oyy1.real, oyy1.imag,
                                        txy1.real, txy1.imag,
                                        ' ' * ni,
                                        oxx2.real, oxx2.imag, oyy2.real, oyy2.imag,
                                        txy2.real, txy2.imag,
                                    ))
                            msg += ('%s     (%s, %sj, %s, %sj, %s, %sj)\n'
                                    % (
                                        ' ' * ni,
                                        oxx1.real - oxx2.real, oxx1.imag - oxx2.imag,
                                        oyy1.real - oyy2.real, oyy1.imag - oyy2.imag,
                                        txy1.real - txy2.real, txy1.imag - txy2.imag,
                                    ))

                            i += 1
                        if i > 10:
                            print(msg)
                            raise ValueError(msg)
            else:
                raise NotImplementedError(self.is_sort2)
            if i > 0:
                print(msg)
                raise ValueError(msg)
        return True

    def add_sort1(self, dt, eid, node_id,
                  fdr1, oxx1, oyy1, txy1, ovm1,
                  fdr2, oxx2, oyy2, txy2, ovm2) -> None:
        assert isinstance(eid, integer_types) and eid > 0, 'dt=%s eid=%s' % (dt, eid)
        self._times[self.itime] = dt
        #print(self.element_types2, element_type, self.element_types2.dtype)
        #print('itotal=%s dt=%s eid=%s nid=%-5s oxx=%s' % (self.itotal, dt, eid, node_id, oxx))

        assert isinstance(node_id, int), node_id
        self.data[self.itime, self.itotal] = [oxx1, oyy1, txy1, ovm1]
        self.element_node[self.itotal, :] = [eid, node_id]  # 0 is center
        self.fiber_distance[self.itotal] = fdr1
        #self.ielement += 1
        self.itotal += 1

        self.data[self.itime, self.itotal] = [oxx2, oyy2, txy2, ovm2]
        self.element_node[self.itotal, :] = [eid, node_id]  # 0 is center
        self.fiber_distance[self.itotal] = fdr2
        self.itotal += 1
        #self.ielement += 1

    def add_sort2(self, dt, eid, nid,
                  fd1, oxx1, oyy1, txy1, ovm1,
                  fd2, oxx2, oyy2, txy2, ovm2) -> None:
        nnodes = self.nnodes_per_element
        itime = self.ielement // nnodes
        inid = self.ielement % nnodes
        #itotal = self.itotal
        ielement = self.itime
        #print(f'itime={itime} eid={eid} nid={nid}; inid={inid} ielement={ielement} - {self.element_name}-{self.element_type}')

        #ibase = 2 * ielement # ctria3/cquad4-33
        ibase = 2 * (ielement * nnodes + inid)
        ie_upper = ibase
        ie_lower = ibase + 1

        #debug = False
        self._times[itime] = dt
        #print(self.element_types2, element_type, self.element_types2.dtype)

        #itime = self.ielement
        #itime = self.itime
        #ielement = self.itime
        assert isinstance(eid, integer_types) and eid > 0, 'dt=%s eid=%s' % (dt, eid)

        if 1:
            if itime == 0:
                self.element_node[ie_upper, :] = [eid, nid]  # 0 is center
                self.element_node[ie_lower, :] = [eid, nid]  # 0 is center
                self.fiber_distance[ie_upper] = fd1
                self.fiber_distance[ie_lower] = fd2
            self.data[itime, ie_upper, :] = [oxx1, oyy1, txy1, ovm1]
            self.data[itime, ie_lower, :] = [oxx2, oyy2, txy2, ovm2]

        self.itotal += 2
        self.ielement += 1
        #if debug:
            #print(self.element_node)

    def get_stats(self, short: bool=False) -> List[str]:
        if not self.is_built:
            return [
                '<%s>\n' % self.__class__.__name__,
                f'  ntimes: {self.ntimes:d}\n',
                f'  ntotal: {self.ntotal:d}\n',
            ]

        nelements = self.nelements
        ntimes = self.ntimes
        nnodes = self.element_node.shape[0]
        #ntotal = self.ntotal
        msg = []
        if self.nonlinear_factor not in (None, np.nan):  # transient
            msg.append('  type=%s ntimes=%i nelements=%i nnodes=%i; table_name=%r\n' % (
                self.__class__.__name__, ntimes, nelements, nnodes, self.table_name))
        else:
            msg.append('  type=%s nelements=%i nnodes=%i; table_name=%r\n' % (
                self.__class__.__name__, nelements, nnodes, self.table_name))
        msg.append('  eType, cid\n')
        headers = self._get_headers()
        nheaders = len(headers)
        headers_str = ', '.join(headers)
        msg.append(f'  data: [ntimes, nnodes, {nheaders}] where {nheaders}=[{headers_str}]\n')
        msg.append(f'  element_node.shape = {self.element_node.shape}\n')
        msg.append(f'  data.shape = {self.data.shape}\n')
        msg.append(f'  {self.element_name}-{self.element_type}\n')
        msg += self.get_data_code()
        return msg

    def write_f06(self, f06_file, header=None, page_stamp='PAGE %s',
                  page_num=1, is_mag_phase=False, is_sort1=True) -> int:
        if header is None:
            header = []
        msg_temp, nnodes, is_bilinear = _get_plate_msg(self, is_mag_phase, is_sort1)
        if self.is_von_mises:
            warnings.warn(f'{self.class_name} doesnt support writing von Mises')
            f06_file.write(f'{self.class_name} doesnt support writing von Mises\n')

        ntimes = self.data.shape[0]
        for itime in range(ntimes):
            dt = self._times[itime]

            dt_line = ' %14s = %12.5E\n' % (self.data_code['name'], dt)
            header[1] = dt_line
            msg = header + msg_temp
            f06_file.write('\n'.join(msg))

            if self.element_type == 144: # CQUAD4 bilinear
                self._write_f06_quad4_bilinear_transient(f06_file, itime, 4, is_mag_phase, 'CEN/4')
            elif self.element_type in [33, 74, 227, 228]:
                # CQUAD4 linear, CTRIA3, CTRIAR linear, CQUADR linear
                self._write_f06_tri3_transient(f06_file, itime, is_mag_phase)
            elif self.element_type == 64:  #CQUAD8
                self._write_f06_quad4_bilinear_transient(f06_file, itime, 5, is_mag_phase, 'CEN/8')
            elif self.element_type == 82:  # CQUADR
                self._write_f06_quad4_bilinear_transient(f06_file, itime, 5, is_mag_phase, 'CEN/8')
            elif self.element_type == 70:  # CTRIAR
                self._write_f06_quad4_bilinear_transient(f06_file, itime, 3, is_mag_phase, 'CEN/3')
            elif self.element_type == 75:  # CTRIA6
                self._write_f06_quad4_bilinear_transient(f06_file, itime, 3, is_mag_phase, 'CEN/6')
            else:
                raise NotImplementedError('name=%r type=%s' % (self.element_name, self.element_type))

            f06_file.write(page_stamp % page_num)
            page_num += 1
        return page_num - 1

    def _write_f06_tri3_transient(self, f06_file, itime, is_magnitude_phase) -> None:
        """
        CQUAD4 linear
        CTRIA3
        """
        fds = self.fiber_distance
        oxx = self.data[itime, :, 0]
        oyy = self.data[itime, :, 1]
        txy = self.data[itime, :, 2]
        ovm = self.data[itime, :, 3]

        eids = self.element_node[:, 0]

        ilayer0 = True
        for eid, fd, doxx, doyy, dtxy, dovm in zip(eids, fds, oxx, oyy, txy, ovm):
            fdr = write_float_13e(fd)
            [oxxr, oyyr, txyr,
             oxxi, oyyi, txyi,] = write_imag_floats_13e([doxx, doyy, dtxy], is_magnitude_phase)

            if ilayer0:    # TODO: assuming 2 layers?
                f06_file.write('0  %6i   %-13s     %-13s / %-13s     %-13s / %-13s     %-13s / %s\n' % (
                    eid, fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
            else:
                f06_file.write('   %6s   %-13s     %-13s / %-13s     %-13s / %-13s     %-13s / %s\n' % (
                    '', fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
            ilayer0 = not ilayer0

    def _write_f06_quad4_bilinear_transient(self, f06_file, itime,
                                            unused_n, is_magnitude_phase, cen) -> None:
        """
        CQUAD4 bilinear
        CQUAD8
        CTRIAR
        CTRIA6
        """
        fds = self.fiber_distance
        oxx = self.data[itime, :, 0]
        oyy = self.data[itime, :, 1]
        txy = self.data[itime, :, 2]
        ovm = self.data[itime, :, 3]

        eids = self.element_node[:, 0]
        nodes = self.element_node[:, 1]

        ilayer0 = True
        for eid, node, fd, doxx, doyy, dtxy, dovm in zip(eids, nodes, fds, oxx, oyy, txy, ovm):
            fdr = write_float_13e(fd)
            [oxxr, oyyr, txyr,
             oxxi, oyyi, txyi,] = write_imag_floats_13e([doxx, doyy, dtxy], is_magnitude_phase)

            if node == 0 and ilayer0:
                f06_file.write('0  %8i %8s  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n' % (
                    eid, cen, fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
            elif ilayer0:    # TODO: assuming 2 layers?
                f06_file.write('   %8s %8i  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n' % (
                    '', node, fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
            else:
                f06_file.write('   %8s %8s  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n\n' % (
                    '', '', fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
            ilayer0 = not ilayer0

    def write_op2(self, op2_file, op2_ascii, itable, new_result,
                  date, is_mag_phase=False, endian='>') -> int:
        """writes an OP2"""
        import inspect
        from struct import Struct, pack
        frame = inspect.currentframe()
        call_frame = inspect.getouterframes(frame, 2)
        op2_ascii.write(f'{self.__class__.__name__}.write_op2: {call_frame[1][3]}\n')

        if itable == -1:
            self._write_table_header(op2_file, op2_ascii, date)
            itable = -3

        nnodes = self.nnodes_per_element
        #print("nnodes =", self.element_name, nnodes)
        #cen_word_ascii = 'CEN/%i' % nnodes
        #cen_word = b'CEN/%i' % nnodes

        #msg.append(f'  element_node.shape = {self.element_node.shape}\n')
        #msg.append(f'  data.shape={self.data.shape}\n')

        eids = self.element_node[:, 0]
        #nids = self.element_node[:, 1]

        eids_device = eids * 10 + self.device_code

        nelements = len(np.unique(eids))
        #print('nelements =', nelements)
        # 21 = 1 node, 3 principal, 6 components, 9 vectors, 2 p/ovm
        #ntotal = ((nnodes * 21) + 1) + (nelements * 4)

        ntotali = self.num_wide
        ntotal = ntotali * nelements

        #print('shape = %s' % str(self.data.shape))
        #assert nnodes > 1, nnodes
        #assert self.ntimes == 1, self.ntimes

        #device_code = self.device_code
        op2_ascii.write(f'  ntimes = {self.ntimes}\n')

        #fmt = '%2i %6f'
        #print('ntotal=%s' % (ntotal))
        #assert ntotal == 193, ntotal

        #[fiber_dist, oxx, oyy, txy, angle, majorP, minorP, ovm]
        op2_ascii.write('  #elementi = [eid_device, node, fds, oxx, oyy, txy...\n')

        if self.is_sort1:
            struct1 = Struct(endian + b'i 4s i 8f')
            struct2 = Struct(endian + b'i 8f')
            struct3 = Struct(endian + b'8f')
        else:
            raise NotImplementedError('SORT2')

        op2_ascii.write(f'nelements={nelements:d}\n')
        if nnodes == 1: # CTRIA3 centroid
            itable = self._write_op2_ctria3(
                op2_file, op2_ascii, new_result, itable,
                ntotal, eids_device)
            return itable
        for itime in range(self.ntimes):
            self._write_table_3(op2_file, op2_ascii, new_result, itable, itime)

            # record 4
            itable -= 1
            header = [4, itable, 4,
                      4, 1, 4,
                      4, 0, 4,
                      4, ntotal, 4,
                      4 * ntotal]
            op2_file.write(pack('%ii' % len(header), *header))
            op2_ascii.write('r4 [4, 0, 4]\n')
            op2_ascii.write(f'r4 [4, {itable:d}, 4]\n')
            op2_ascii.write(f'r4 [4, {4 * ntotal:d}, 4]\n')

            fds = self.fiber_distance
            oxx = self.data[itime, :, 0]
            oyy = self.data[itime, :, 1]
            txy = self.data[itime, :, 2]
            ovm = self.data[itime, :, 3]

            eids = self.element_node[:, 0]
            nodes = self.element_node[:, 1]

            ilayer0 = True
            nwide = 0

            for eid_device, eid, node, fd, doxx, doyy, dtxy, dovm in zip(eids_device, eids, nodes, fds, oxx, oyy, txy, ovm):
                if node == 0 and ilayer0:
                    data = [eid_device, b'CEN/', node, fd,
                            doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag,
                            dovm.real]
                    op2_file.write(struct1.pack(*data))
                    op2_ascii.write('eid=%s node=%s data=%s' % (eid, node, str(data[2:])))
                    #f06_file.write('0  %8i %8s  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n' % (
                        #eid, cen, fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
                elif ilayer0:    # TODO: assuming 2 layers?
                    data = [node, fd,
                            doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag,
                            dovm.real]
                    op2_file.write(struct2.pack(*data))
                    op2_ascii.write('  node=%s data=%s' % (node, str(data[2:])))
                    #f06_file.write('   %8s %8i  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n' % (
                        #'', node, fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
                else:
                    data = [fd,
                            doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag,
                            dovm.real]
                    op2_file.write(struct3.pack(*data))
                    op2_ascii.write('    data=%s' % (str(data[2:])))
                    #f06_file.write('   %8s %8s  %-13s   %-13s / %-13s   %-13s / %-13s   %-13s / %s\n\n' % (
                        #'', '', fdr, oxxr, oxxi, oyyr, oyyi, txyr, txyi))
                ilayer0 = not ilayer0
                nwide += len(data)

            assert nwide == ntotal, f'nwide={nwide} ntotal={ntotal}'
            itable -= 1
            header = [4 * ntotal,]
            op2_file.write(pack('i', *header))
            op2_ascii.write('footer = %s\n' % header)
            new_result = False
        return itable

    def _write_op2_ctria3(self, op2_file, op2_ascii, new_result, itable,
                          ntotal, eids_device) -> int:
        struct1 = Struct(b'i 8f')
        struct2 = Struct(b'8f')
        for itime in range(self.ntimes):
            self._write_table_3(op2_file, op2_ascii, new_result, itable, itime)
            # record 4
            itable -= 1
            header = [4, itable, 4,
                      4, 1, 4,
                      4, 0, 4,
                      4, ntotal, 4,
                      4 * ntotal]
            op2_file.write(pack('%ii' % len(header), *header))
            op2_ascii.write('r4 [4, 0, 4]\n')
            op2_ascii.write(f'r4 [4, {itable:d}, 4]\n')
            op2_ascii.write(f'r4 [4, {4 * ntotal:d}, 4]\n')

            fds = self.fiber_distance
            oxx = self.data[itime, :, 0]
            oyy = self.data[itime, :, 1]
            txy = self.data[itime, :, 2]
            ovm = self.data[itime, :, 3]

            eids = self.element_node[:, 0]
            #nodes = self.element_node[:, 1]

            ilayer0 = True
            nwide = 0

            ovm = self.data[itime, :, 3]
            for eid_device, eid, fd, doxx, doyy, dtxy, dovm in zip(eids_device, eids, fds, oxx, oyy, txy, ovm):
                #ilyaer0 = True
                if ilayer0:
                    ndatai = 0
                    data = [eid_device, fd,
                            doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag,
                            dovm.real]
                    op2_file.write(struct1.pack(*data))
                    #op2_ascii.write('eid=%s node=%s data=%s' % (eid, node, str(data[2:])))
                    op2_ascii.write('0  %6i   %-13s     %-13s / %-13s     %-13s / %-13s     %-13s / %s\n' % (
                        eid, fd, doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag, ))
                else:
                    data = [fd,
                            doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag,
                            dovm.real]
                    op2_file.write(struct2.pack(*data))
                    #op2_ascii.write('    data=%s' % (str(data[2:])))
                    op2_ascii.write('   %6s   %-13s     %-13s / %-13s     %-13s / %-13s     %-13s / %s\n' % (
                        '', fd, doxx.real, doxx.imag, doyy.real, doyy.imag, dtxy.real, dtxy.imag))
                ndatai += len(data)
                ilayer0 = not ilayer0
                nwide += len(data)
            assert nwide == ntotal, f"numwide={self.num_wide} ndatai={ndatai} nwide={nwide} ntotal={ntotal} headers={self.get_headers()}"
            itable -= 1
            header = [4 * ntotal,]
            op2_file.write(pack('i', *header))
            op2_ascii.write('footer = %s\n' % header)
            new_result = False
        return itable

def _get_plate_msg(self, is_mag_phase=True, is_sort1=True) -> Tuple[List[str], int, bool]:
    #if self.is_von_mises:
        #von_mises = 'VON MISES'
    #else:
        #von_mises = 'MAX SHEAR'

    if self.is_stress:
        if self.is_fiber_distance:
            grid_msg_temp = ['    ELEMENT              FIBER                                  - STRESSES IN ELEMENT  COORDINATE SYSTEM -\n',
                             '      ID      GRID-ID   DISTANCE                 NORMAL-X                        NORMAL-Y                       SHEAR-XY\n']
            fiber_msg_temp = ['  ELEMENT       FIBRE                                     - STRESSES IN ELEMENT  COORDINATE SYSTEM -\n',
                              '    ID.        DISTANCE                  NORMAL-X                          NORMAL-Y                         SHEAR-XY\n']
        else:
            grid_msg_temp = ['    ELEMENT              FIBRE                                  - STRESSES IN ELEMENT  COORDINATE SYSTEM -\n',
                             '      ID      GRID-ID   CURVATURE                NORMAL-X                        NORMAL-Y                       SHEAR-XY\n']
            fiber_msg_temp = ['  ELEMENT       FIBRE                                     - STRESSES IN ELEMENT  COORDINATE SYSTEM -\n',
                              '    ID.       CURVATURE                  NORMAL-X                          NORMAL-Y                         SHEAR-XY\n']
    else:
        if self.is_fiber_distance:
            grid_msg_temp = ['    ELEMENT              FIBER                                  - STRAINS IN ELEMENT  COORDINATE SYSTEM -\n',
                             '      ID      GRID-ID   DISTANCE                 NORMAL-X                        NORMAL-Y                       SHEAR-XY\n']
            fiber_msg_temp = ['  ELEMENT       FIBRE                                     - STRAINS IN ELEMENT  COORDINATE SYSTEM -\n',
                              '    ID.        DISTANCE                  NORMAL-X                          NORMAL-Y                         SHEAR-XY\n']
        else:
            grid_msg_temp = ['    ELEMENT              FIBRE                                  - STRAINS IN ELEMENT  COORDINATE SYSTEM -\n',
                             '      ID      GRID-ID   CURVATURE                NORMAL-X                        NORMAL-Y                       SHEAR-XY\n']
            fiber_msg_temp = ['  ELEMENT       FIBRE                                     - STRAINS IN ELEMENT  COORDINATE SYSTEM -\n',
                              '    ID.       CURVATURE                  NORMAL-X                          NORMAL-Y                         SHEAR-XY\n']


    if is_mag_phase:
        mag_real = ['                                                         (MAGNITUDE/PHASE)\n \n']
    else:
        mag_real = ['                                                          (REAL/IMAGINARY)\n', ' \n']

    ## TODO: validation on header formatting...
    if self.is_stress:
        cquad4_bilinear = ['                C O M P L E X   S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN  \n \n']
        cquad4_centroid = ['                C O M P L E X   S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )\n']  # good
        cquad8 = ['                C O M P L E X   S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 8 )\n']
        cquadr = ['                C O M P L E X   S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D R )\n']
        ctria3 = ['                   C O M P L E X   S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )\n']  # good
        ctria6 = ['                   C O M P L E X   S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 6 )\n']
        ctriar = ['                   C O M P L E X   S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A R )\n']
    else:
        cquad4_bilinear = ['                C O M P L E X   S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN  \n \n']
        cquad4_centroid = ['                C O M P L E X   S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )\n']
        cquad8 = ['                C O M P L E X   S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 8 )\n']
        cquadr = ['                C O M P L E X   S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D R )\n']
        ctria3 = ['                C O M P L E X   S T R A I N S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )\n']
        ctria6 = ['                C O M P L E X   S T R A I N S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 6 )\n']
        ctriar = ['                C O M P L E X   S T R A I N S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A R )\n']

    msg = []
    is_bilinear = False
    if self.element_type == 144: # CQUAD4
        is_bilinear = True
        msg += cquad4_bilinear + mag_real + grid_msg_temp
    elif self.element_type == 33: # CQUAD4
        is_bilinear = False
        msg += cquad4_centroid + mag_real + fiber_msg_temp
    elif self.element_type == 64:  #CQUAD8
        msg += cquad8 + mag_real + grid_msg_temp
        is_bilinear = True
    elif self.element_type == 82:  # CQUADR
        msg += cquadr + mag_real + grid_msg_temp
        is_bilinear = True

    elif self.element_type == 74: # CTRIA3
        msg += ctria3 + mag_real + fiber_msg_temp
    elif self.element_type == 75:  # CTRIA6
        msg += ctria6 + mag_real + grid_msg_temp
        is_bilinear = True
    elif self.element_type == 70:  # CTRIAR
        msg += ctriar + mag_real + grid_msg_temp
        is_bilinear = True
    elif self.element_type == 227:  # CTRIAR
        msg += ctriar + mag_real + grid_msg_temp
        is_bilinear = False
    elif self.element_type == 228:  # CQUADR
        msg += cquadr + mag_real + grid_msg_temp
        is_bilinear = False
    else:
        raise NotImplementedError(f'name={self.element_name!r} type={self.element_type}')

    nnodes = get_nnodes(self)
    return msg, nnodes, is_bilinear

def get_nnodes(self):
    if self.element_type in [64, 82, 144]:  # ???, CQUADR, CQUAD4 bilinear
        nnodes = 4 + 1 # centroid
    elif self.element_type in [70, 75]:   #???, CTRIA6
        nnodes = 3 + 1 # centroid
    elif self.element_type in [33, 74, 227, 228]:  # CTRIA3, CQUAD4 linear, CQUADR linear, CQUADR linear
        nnodes = 1
    else:
        raise NotImplementedError(f'name={self.element_name!r} type={self.element_type}')
    return nnodes

class ComplexPlateVMStressArray(ComplexPlateVMArray, StressObject):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ComplexPlateVMArray.__init__(self, data_code, is_sort1, isubcase, dt)
        StressObject.__init__(self, data_code, isubcase)

    def _get_headers(self):
        headers = ['oxx', 'oyy', 'txy', 'ovm']
        return headers

    def get_headers(self) -> List[str]:
        return self._get_headers()


class ComplexPlateVMStrainArray(ComplexPlateVMArray, StrainObject):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ComplexPlateVMArray.__init__(self, data_code, is_sort1, isubcase, dt)
        StrainObject.__init__(self, data_code, isubcase)
        assert self.is_strain, self.stress_bits

    def _get_headers(self):
        headers = ['exx', 'eyy', 'exy', 'evm']
        return headers

    def get_headers(self) -> List[str]:
        return self._get_headers()
