#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""data for all cycles and utilities to identify them"""
import functools as fnt
from typing import Iterable, Union, Tuple, Optional

import numpy as np
import pandas as pd


def crc_velocity(V: Iterable, crc: Union[int, str] = 0, full=False) -> str:
    """
    Compute the CRC32(V * 10) of a 1Hz velocity trace.

    :param V:
        velocity samples, to be rounded according to :data:`wltp.invariants.v_decimals`
    :param crc:
        initial CRC value (might be a hex-string)
    :param full:
        print full 32bit number (x8 hex digits), or else, 
        just the highest half (the 1st x4 hex digits)
    :return:
         the 16 lowest bits of the CRC32 of the trace, as hex-string

    1. The velocity samples are first round to `v_decimals`;
    2. the samples are then multiplied x10 to convert into integers
       (assuming `v_decimals` is 1);
    3. the integer velocity samples are then converted into int16 little-endian bytes
       (eg 0xC0FE --> (0xFE, 0xC0);
    4. the int16 bytes are then concatanated together, and
    5. fed into ZIP's CRC32;
    6. the highest 2 bytes of the CRC32 are (usually) kept, formated in hex 
       (x4 leftmost hex-digits).

    """
    from binascii import crc32  # it's the same as `zlib.crc32`
    from ..invariants import v_decimals, vround

    if not isinstance(V, pd.Series):
        V = pd.Series(V)
    if isinstance(crc, str):
        crc = int(crc, 16)

    V_ints = vround(V) * 10 ** v_decimals
    vbytes = V_ints.astype(np.int16).values.tobytes()
    crc = hex(crc32(vbytes, crc)).upper()

    crc = crc[2:] if full else crc[2:6]
    return crc


@fnt.lru_cache()
def cycle_checksums(full=False) -> pd.DataFrame:
    """
    Return a big table with cummulative and simple SUM & CRC for all class phases.
    
    :param full:
        CRCs contain the full 32bit number (x8 hex digits)

    """
    import io
    from textwrap import dedent
    from pandas import IndexSlice as idx

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    table_csv = dedent(
        """
        checksum		CRC32	CRC32	CRC32	CRC32	CRC32	CRC32	SUM	SUM
        accumulation		by_phase	by_phase	by_phase	cummulative	cummulative	cummulative	by_phase	cummulative
        phasing		V	VA0	VA1	V	VA0	VA1	V	V
        class	part								
        class1	part-1	9840D3E9	4438BBA3	97DBE17C	9840D3E9	4438BBA3	97DBE17C	11988.4	11988.4
        class1	part-2	8C342DB0	8C8D3B61	D9E87FE5	DCF2D584	90BEA9C	4295031D	17162.8	29151.2
        class1	part-3	9840D3E9	9840D3E9	97DBE17C	6D1D7DF5	6D1D7DF5	F523E31C	11988.4	41139.6
        class2	part-1	85914C5F	CDD16179	8A0A7ECA	85914C5F	CDD16179	8A0A7ECA	11162.2	11162.2
        class2	part-2	312DBBFF	391AA607	64F1E9AA	A0103D21	606EFF7B	3E77EBB8	17054.3	28216.5
        class2	part-3	81CD4DA6	E29E35E8	9560F88E	28FBF6C3	926135F3	D162E0F1	24450.6	52667.1
        class2	part-4	8994F1E9	8994F1E9	2181BF4D	474B3569	474B3569	F70F32D3	28869.8	81536.9
        class3a	part-1	48E5AA11	910CE01B	477E9884	48E5AA11	910CE01B	477E9884	11140.3	11140.3
        class3a	part-2	14945FDD	D93BFCA7	41480D88	403DF278	24879CA6	DE5A24E1	16995.7	28136.0
        class3a	part-3	8B3B20BE	9887E03D	9F969596	D7708FF4	3F6732E0	2EE999C6	25646.0	53782.0
        class3a	part-4	F9621B4F	F9621B4F	517755EB	9BCE354C	9BCE354C	2B8A32F6	29714.9	83496.9
        class3b	part-1	48E5AA11	910CE01B	477E9884	48E5AA11	910CE01B	477E9884	11140.3	11140.3
        class3b	part-2	AF1D2C10	E50188F1	FAC17E45	FBB481B5	18BDE8F0	65D3572C	17121.2	28261.5
        class3b	part-3	15F6364D	A779B4D1	15B8365	43BC555F	B997EE4D	BA25436D	25782.2	54043.7
        class3b	part-4	F9621B4F	F9621B4F	517755EB	639BD037	639BD037	D3DFD78D	29714.9	83758.6
        """
    )
    df = pd.read_csv(
        io.StringIO(table_csv), sep="\t", header=[0, 1, 2], index_col=[0, 1]
    )
    if not full:

        def clip_crc(sr):
            try:
                sr = sr.str[:4]
            except AttributeError:
                # AttributeError('Can only use .str accessor with string values...
                pass
            return sr

        df = df.groupby(level="checksum", axis=1).transform(clip_crc)

    return df


@fnt.lru_cache()
def cycle_phases() -> pd.DataFrame:
    """Return a textual table with the boundaries of all phaes and cycle *phasings*"""
    import io
    from textwrap import dedent
    from pandas import IndexSlice as idx

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    table_csv = dedent(
        """
        class	phasing	part-1	part-2	part-3	part-4
        class1	V	[0, 589]	[589, 1022]	[1022, 1612]	
        class1	VA0	[0, 588]	[589, 1021]	[1022, 1611]	
        class1	VA1	[1, 589]	[590, 1022]	[1023, 1612]	
        class2	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1801]
        class2	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1800]
        class2	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1801]
        class3a	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1801]
        class3a	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1800]
        class3a	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1801]
        class3b	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1801]
        class3b	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1800]
        class3b	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1801]
        """
    )
    return pd.read_csv(
        io.StringIO(table_csv), sep="\t", header=0, index_col=[0, 1]
    ).fillna("")


def identify_cycle_v_crc(
    crc: Union[int, str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """see :func:`identify_cycle_v()`"""
    if isinstance(crc, str):
        crc = int(crc, 16)
    crc = hex(crc).upper()
    crc = crc[2:6]

    crcs = cycle_checksums(full=False)["CRC32"]
    matches = crcs == crc
    if matches.any(None):
        ## Fetch 1st from top-left.
        #
        for col, flags in matches.iteritems():
            if flags.any():
                index = np.asscalar(next(iter(np.argwhere(flags))))
                cycle, part = crcs.index[index]
                accum, phasing = col
                if accum == "cummulative":
                    if index in [2, 6, 10, 14]:  # is it a final cycle-part?
                        part = None
                    else:
                        part = part.upper()

                return (cycle, part, phasing)
        else:
            assert False, ("Impossible find:", crc, crcs)
    return (None, None, None)


def identify_cycle_v(V: Iterable):
    """
    Finds which cycle/part/kind matches a CRC.

    :param V:
        Any cycle or parts of it (one of Low/Medium/High/Extra Kigh phases), 
        or concatenated subset of the above phases, but in that order.
    :return:
        a 3 tuple (class, part, kind), like this:

        - ``(None,     None,   None)``: if no match
        - ``(<class>,  None,  <phasing>)``: if it matches a full-cycle
        - ``(<class>, <part>, <phasing>)``: if it matches a part
        - ``(<class>, <PART>, <phasing>)``: (CAPITAL part) if it matches a part cummulatively

        where `<phasing>` is one of 
        
        - ``V`` 
        - ``A0`` (offset: 0, length: -1) 
        - ``A1`` (offset: 1, length: -1)
   """
    crc = crc_velocity(V)
    return identify_cycle_v_crc(crc)
