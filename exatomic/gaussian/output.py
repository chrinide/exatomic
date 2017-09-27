## -*- coding: utf-8 -*-
## Copyright (c) 2015-2016, Exa Analytics Development Team
## Distributed under the terms of the Apache License 2.0
#"""
#Gaussian Output Editor
##########################
#Editor classes for various types of Gaussian output files
#"""
#<<<<<<< HEAD
##import re
##import numpy as np
##import pandas as pd
##from io import StringIO
##
##from exatomic import Length
##from .editor import Editor
##from exa.relational.isotope import z_to_symbol
##from exatomic import Energy
##from exatomic.frame import compute_frame_from_atom
##from exatomic.algorithms.basis import lmap
##
##z_to_symbol = z_to_symbol()
##
##from numba import jit, int64
##@jit(nopython=True, cache=True)
##def _triangular_indices(ncol, nbas, ndim):
##    idx = np.empty((dim, 3), dtype=np.int64)
##    cnt = 0
##    for i in range(ncol):
##        for j in range(i, nbas, ncol):
##            for k in range(j, nbas):
##                idx[cnt,0] = j
##                idx[cnt,1] = k
##                idx[cnt,2] = 0
##                cnt += 1
##    return idx
##
##class Output(Editor):
##
##    def _parse_triangular_matrix(self, regex, column='coef', values_only=False):
##        found = self.find_next(_rebas02, keys_only=True)
##        nbas = int(self[found].split()[0])
##        found = self.find_next(regex, keys_only=True)
##        if not found: return
##        ncol = len(self[found + 1].split())
##        start = found + 2
##        rmdr = nbas % ncol
##        skips = np.array(list(reversed(range(rmdr, nbas + rmdr, ncol))))
##        skips = np.cumsum(skips) + np.arange(len(skips))
##        stop = start + skips[-1]
##        matrix = self.pandas_dataframe(start, stop, ncol + 1,
##                                       index_col=0, skiprows=skips,
##                                       ).unstack().dropna().apply(
##                                       lambda x: x.replace('D', 'E')
##                                       ).astype(np.float64).values
##        if values_only: return matrix
##        idxs = _triangular_indices(ncol, nbas, matrix.shape[0])
##        return pd.DataFrame.from_dict({'chi0': idxs[:,0],
##                                       'chi1': idxs[:,1],
##                                      'frame': idxs[:,2],
##                                       column: matrix})
##
##    def parse_atom(self):
##        # Find our data
##        found = self.find(_regeom01, _regeom02, keys_only=True)
##        # Check if nosymm was specified
##        key = _regeom02 if found[_regeom02] else _regeom01
##        starts = np.array(found[key]) + 5
##        # Prints converged geometry twice but only need it once
##        starts = starts[:-1] if len(starts) > 1 else starts
##        stop = starts[0]
##        # Find where the data stops
##        while '-------' not in self[stop]: stop += 1
##        # But it should be same sized array each time
##        stops = starts + (stop - starts[0])
##        dfs = []
##        # Iterate over frames
##        for i, (start, stop) in enumerate(zip(starts, stops)):
##            atom = self.pandas_dataframe(start, stop, 6)
##            atom['frame'] = i
##            dfs.append(atom)
##        atom = pd.concat(dfs).reset_index(drop=True)
##        # Drop the column of atomic type (whatever that is)
##        atom.drop([2], axis=1, inplace=True)
##        # Name the data
##        atom.columns = ['set', 'Z', 'x', 'y', 'z', 'frame']
##        # Zero-based indexing
##        atom['set'] -= 1
##        # Convert to atomic units
##        atom['x'] *= Length['A', 'au']
##        atom['y'] *= Length['A', 'au']
##        atom['z'] *= Length['A', 'au']
##        # Map atomic symbols onto Z numbers
##        atom['symbol'] = atom['Z'].map(z_to_symbol)
##        self.atom = atom
##
##    def parse_basis_set(self):
##        # First check if gfinput was specified
##        check = self.regex(_rebas01, stop=1000, flags=re.IGNORECASE)
##        if not check: return
##        # Find where the basis set is printed
##        found = self.find(_rebas02[:-1], _rebas03)
##        stop = found[_rebas02[:-1]][0][0] - 1
##        start = stop - 1
##        # Find where the data actually starts
##        while not len(self[start].split()) > 4: start -= 1
##        # Call out to the mess that actually parses it
##        df = self.pandas_dataframe(start + 1, stop, 4)
##        self.basis_set, setmap = _basis_set(df)
##        # Map the unique basis sets on atomic centers
##        self.atom['set'] = self.atom['set'].map(setmap)
##
##    def parse_orbital(self):
##        # Find where our data is
##        found = self.regex(_reorb01, _reorb02, _rebas02)
##        # Basis dimension
##        nbas = int(found[_rebas02][0][1].split()[0])
##        # If no orbital energies, quit
##        if not found[_reorb01]: return
##        # Check if open shell
##        os = any(('Beta' in ln for lno, ln in found[_reorb01]))
##        # Find out how big our data is
##        # 5 eigenvalues are printed per line
##        nrows = len(found[_reorb01]) * 5 // nbas
##        nsets = nrows // 2 if os else nrows
##        # Allocate a numpy array to store it
##        # index is arbitrary for the momentum
##        dtypes = [('energy', 'f8'), ('occupation', 'f8'), ('vector', 'f8'),
##                  ('spin', 'i8'), ('group', 'i8')]
##        data = np.empty((nbas * nrows,), dtype=dtypes)
##        cnt, vec, grp = 0, 0, 0
##        grpchk = 2 * nbas if os else nbas
##        # Populate and increment accordingly
##        for lno, ln in found[_reorb01]:
##            for i in _orbslice:
##                en = ln[28:][i]
##                if en:
##                    if 'occ' in ln:
##                        occ = 1 if os else 2
##                    else: occ = 0
##                    spn = 0 if 'Alpha' in ln else 1
##                    data[cnt] = (en, occ, vec, spn, grp)
##                    cnt += 1
##                    vec += 1
##                    if cnt == grpchk: grp += 1
##                    if vec == nbas: vec = 0
##        orbital = pd.DataFrame(data)
##        # Still no good way of dealing with multiple orbital sets per frame
##        # Handled temporarily by the use of 'index' rather than 'frame'
##        #frmstride = nbas * 2 if os else nbas
##        #orbital['frame'] = np.repeat(range(len(orbital)//frmstride), frmstride)
##        orbital['frame'] = 0
##        # Symmetry labels
##        if found[_reorb02]:
##            # Gaussian seems to print out a lot of these blocks
##            # try to get a handle on them
##            if len(found[_reorb02]) != nsets:
##                if nsets == 1:
##                    found[_reorb02] = found[_reorb02][-1:]
##                elif nsets == 2:
##                    found[_reorb02] = found[_reorb02][:1] + found[_reorb02][-1:]
##                else:
##                    print('Mismatch in eigenvalue and symmetry blocks. '
##                          'Continuing without symmetry.')
##                    found[_reorb02] = []
##            allsyms = []
##            match = ['(', 'Orbitals']
##            for i, (start, ln) in enumerate(found[_reorb02]):
##                # Find the start, stop indices for each block
##                while match[0] not in self[start]: start += 1
##                stop = start + 1
##                while any((i in self[stop] for i in match)): stop += 1
##                # Clean up the text block so it is just symmetries
##                syms = _resympat.sub(lambda m: _symrep[m.group(0)],
##                                     ' '.join([i.strip() for i in
##                                     self[start:stop]])).split()
##                # cat the syms for each block together
##                allsyms += syms
##            # Add it to our dataframe
##            orbital['symmetry'] = allsyms
##        self.orbital = orbital
##
##
##    def parse_momatrix(self):
##        """
##        Parses the MO matrix if asked for in the input.
##
##        Note:
##            Requires specification of pop(full) or pop(no) or the like.
##        """
##        if hasattr(self, '_momatrix'): return
##        # Check if a full MO matrix was specified in the input
##        check = self.regex(_remomat01, stop=1000, flags=re.IGNORECASE)
##        if not check: return
##        # Find approximately where our data is
##        found = self.find(_remomat02, _rebas02)
##        # Get some dimensions
##        ndim = len(found[_remomat02])
##        # If something goes wrong
##        if not ndim: return
##        nbas = int(found[_rebas02][0][1].split()[0])
##        nblocks = np.int64(np.ceil(nbas / 5))
##        # Allocate a big ol' array
##        coefs = np.empty((nbas ** 2, ndim), dtype=np.float64)
##        # Dynamic column generation hasn't been worked out yet
##        colnames = ['coef'] + ['coef' + str(i) for i in range(1, ndim)]
##        # Iterate over where the data was found
##        # c counts the column in the resulting momatrix table
##        for c, (lno, ln) in enumerate(found[_remomat02]):
##            start = self.find_next('Eigenvalues', start=lno, keys_only=True) + 1
##            stop = start + nbas
##            # The basis set order is printed with every chunk of eigenvectors
##            if c == 0: self.basis_set_order = _basis_set_order(self[start:stop])
##            # Some fudge factors due to extra lines being printed
##            space = start - lno - 1
##            fnbas = nbas + space
##            span = start + fnbas * nblocks
##            # Finally get where our chunks are
##            starts = np.arange(start, span, fnbas)
##            stops = np.arange(stop, span, fnbas)
##            stride = 0
##            # b counts the blocks of eigenvectors per column in momatrix
##            for b, (start, stop) in enumerate(zip(starts, stops)):
##                # Number of eigenvectors in this block
##                ncol = len(self[start][20:].split())
##                _csv_args['names'] = range(ncol)
##                # Massage the text so that we can read csv
##                block = '\n'.join([ln[20:] for ln in self[start:stop]])
##                block = _rebaspat.sub(lambda m: _basrep[m.group(0)], block)
##                # Enplacen the resultant unstacked values
##                coefs[stride:stride + nbas * ncol, c] = pd.read_csv(
##                    StringIO(block), **_csv_args).unstack().values
##                stride += nbas * ncol
##        # Index chi, phi
##        chis = np.tile(range(nbas), nbas)
##        orbs = np.repeat(range(nbas), nbas)
##        momatrix = pd.DataFrame(coefs, columns=colnames)
##        momatrix['chi'] = chis
##        momatrix['orbital'] = orbs
##        # Frame not really implemented for momatrix
##        momatrix['frame'] = 0
##        self.momatrix = momatrix
##
##    def parse_basis_set_order(self):
##        if hasattr(self, '_basis_set_order'): return
##        self.parse_momatrix()
##
##
##    def parse_frame(self):
##        # Get the default frame from the atom table
##        self.frame = compute_frame_from_atom(self.atom)
##        # Find our data
##        found = self.find(_retoten, _realphaelec, _reelecstate)
##        # Extract just the total SCF energies
##        ens = [float(ln.split()[4]) for lno, ln in found[_retoten]]
##        # If 'SCF Done' prints out more times than frames
##        try:
##            ens = ens if len(self.frame) == len(ens) else ens[-len(self.frame):]
##            self.frame['E_tot'] = ens
##        except:
##            pass
##        # We will assume number of electrons doesn't change per frame
##        ae, x, x, be, x, x = found[_realphaelec][0][1].split()
##        self.frame['N_e'] = int(ae) + int(be)
##        self.frame['N_a'] = int(ae)
##        self.frame['N_b'] = int(be)
##        # Try to get the electronic state but don't try too hard
##        try:
##            states = []
##            for lno, ln in found[_reelecstate]:
##                if 'initial' in ln: continue
##                states.append(ln.split()[4].replace('.', ''))
##            self.frame['state'] = states
##        except (IndexError, ValueError):
##            pass
##
##
##    def parse_excitation(self):
##        chk = self.find(_retddft, stop=1000, keys_only=True)
##        if not chk: return
##        # Find the data
##        found = self.find(_reexcst)
##        # Allocate the array
##        dtype = [('eV', 'f8'), ('osc', 'f8'), ('occ', 'i8'),
##                 ('virt', 'i8'), ('kind', 'O'), ('symmetry', 'O')]
##        data = np.empty((len(found),), dtype=dtype)
##        # Iterate over what we found
##        for i, (lno, ln) in enumerate(found):
##            # Split this line up into what we want and x
##            x, x, x, kind, en, x, x, x, osc, x = ln.split()
##            # Same for the line right after it
##            occ, x, virt, x = self[ln + 1].split()
##            # Assign the values
##            data[i] = (en, osc.replace('f=', ''), occ, virt) + tuple(kind.split('-'))
##        excitation = pd.DataFrame(data)
##        # Internal units dictate we should have Hartrees as 'energy'
##        excitation['energy'] = excitation['eV'] * Energy['eV', 'Ha']
##        # Frame not really implemented here
##        excitation['frame'] = 0
##        excitation['group'] = 0
##        self.excitation = excitation
##
##
##    def parse_frequency(self):
##        found = self.regex(_refreq, stop=1000, flags=re.IGNORECASE)
##        if not found: return
##        # Don't need the input deck or 2 from the summary at the end
##        found = self.find(_refreq)[1:-2]
##        # Total lines per block minus the unnecessary ones
##        span = found[1][0] - found[0][0] - 7
##        dfs, fdx = [], 0
##        # Iterate over what we found
##        for lno, ln in found:
##            # Get the frequencies first
##            freqs = ln[15:].split()
##            nfreqs = len(freqs)
##            # Get just the atom displacement vectors
##            start = lno + 5
##            stop = start + span
##            cols = range(2 + 3 * nfreqs)
##            df = self.pandas_dataframe(start, stop, ncol=cols)
##            # Split up the df and unstack it
##            slices = [list(range(2 + i, 2 + 3 * nfreqs, 3)) for i in range(nfreqs)]
##            dx, dy, dz = [df[i].unstack().values for i in slices]
##            # Generate the appropriate dimensions of other columns
##            labels = np.tile(df[0].values, nfreqs)
##            zs = np.tile(df[1].values, nfreqs)
##            freqdxs = np.repeat(range(fdx, fdx + nfreqs), df.shape[0])
##            freqs = np.repeat(freqs, df.shape[0])
##            fdx += nfreqs
##            # Put it all together
##            stacked = pd.DataFrame.from_dict({'Z': zs, 'label': labels,
##                                    'dx': dx, 'dy': dy, 'dz': dz,
##                                    'frequency': freqs, 'freqdx': freqdxs})
##            stacked['symbol'] = stacked['Z'].map(z_to_symbol)
##            dfs.append(stacked)
##        # Now put all our frequencies together
##        frequency = pd.concat(dfs).reset_index(drop=True)
##        # Pretty sure displacements are in cartesian angstroms
##        # TODO: verify with an external program that vibrational
##        #       modes look the same as the ones generated with
##        #       this methodology.
##        frequency['dx'] *= Length['A', 'au']
##        frequency['dy'] *= Length['A', 'au']
##        frequency['dz'] *= Length['A', 'au']
##        # Frame not really implemented here either
##        frequency['frame'] = 0
##        self.frequency = frequency
##
##
##    def parse_overlap(self):
##        overlap = self._parse_triangular_matrix(_reovl01, 'coef')
##        if overlap is not None: self.overlap = overlap
##
##    def parse_multipole(self):
##        mltpl = self._parse_triangular_matrix(self, _reixn.format(1), 'ix1')
##        if mltpl is not None:
##            mltpl['ix2'] = self._parse_triangular_matrix(self, _reixn.format(2), 'ix2', True)
##            mltpl['ix3'] = self._parse_triangular_matrix(self, _reixn.format(3), 'ix3', True)
##            self.multipole = mltpl
##
##
##    def __init__(self, *args, **kwargs):
##        super().__init__(*args, **kwargs)
##
##
##
##def _basis_set_order(chunk):
##    # Gaussian only prints the atom center
##    # and label once for all basis functions
##    nas = (np.nan, np.nan)
##    lsp = len(chunk[0]) - len(chunk[0].lstrip(' ')) + 2
##    centers = [(ln[lsp:lsp + 3].strip(), ln[lsp + 3:lsp + 6].strip())
##               if ln[lsp:lsp + 3].strip() else nas for ln in chunk]
##    # pandas takes care of that
##    basord = pd.DataFrame(centers, columns=('center', 'tag')).fillna(method='pad')
##    basord['center'] = basord['center'].astype(np.int64)
##    # Zero based indexing
##    basord['center'] -= 1
##    # nlml defines the type of basis function
##    types = '\n'.join([ln[10:20].strip() for ln in chunk])
##    # Gaussian prints 'D 0' so replace with 'D0'
##    types = _rebaspat.sub(lambda m: _basrep[m.group(0)], types)
##    types = pd.Series(types.splitlines())
##    # Now pull it apart into n, l, ml columns
##    split = r"([0-9]{1,})([A-z])(.*)"
##    basord[['n', 'L', 'ml']] = types.str.extract(split, expand=True)
##    # And clean it up -- don't really need n but can use it for shells
##    basord['n'] = basord['n'].astype(np.int64) - 1
##    basord['L'] = basord['L'].str.lower().map(lmap).astype(np.int64)
##    basord['ml'].update(basord['ml'].map({'': 0, 'X': 1, 'Y': -1, 'Z': 0}))
##    basord['ml'] = basord['ml'].astype(np.int64)
##    # Finally get shells -- why so difficult
##    shfns = []
##    shl, pcen, pl, pn = -1, -1, -1, -1
##    for cen, n, l in zip(basord['center'], basord['n'], basord['L']):
##        if not pcen == cen: shl = -1
##        if (not pl == l) or (not pn == n): shl += 1
##        shfns.append(shl)
##        pcen, pl, pn = cen, l, n
##    basord['shell'] = shfns
##    # Get rid of n because it isn't even n anymore
##    del basord['n']
##    return basord
##
##def _basis_set(raw):
##    # Fortran scientific notation
##    raw[0] = raw[0].str.replace('D', 'E')
##    raw[1] = raw[1].str.replace('D', 'E')
##    raw[2] = raw[2].astype('O').str.replace('D', 'E')
##    # But now we replaced the 'D' shell with 'E' so
##    lmap['e'] = 2
##    # The data we need
##    dtype = [('alpha', 'f8'), ('d', 'f8'), ('center', 'i8'),
##             ('shell', 'i8'), ('L', 'i8')]
##    df = np.empty((raw.shape[0],), dtype=dtype)
##    # The data we deserve
##    data = []
##    for i, (one, two) in enumerate(zip(raw[0], raw[1])):
##        # See if it is int-able (an atom center in this case)
##        try:
##            center = int(one) - 1
##        except ValueError:
##            # See if it is a string corresponding to L eg. 'S'
##            if one.isalpha():
##                # Collect (atom, shell, number of primitives, index)
##                data.append((center, one.lower(), int(two), i + 1))
##    # Now through this data (2 loops mainly because of 'sp' shells)
##    cnt, shell, pcntr = 0, 0, 0
##    for cntr, lval, npr, pdx in data:
##        # Reset shell counter if atom changed
##        if pcntr != cntr: shell = 0
##        # l is lval except when lval is 'sp'
##        for c, l in enumerate(lval):
##            l = lmap[l]
##            # Get all the prims per shell
##            for i in range(pdx, pdx + npr):
##                df[cnt] = (raw[0][i], raw[c + 1][i], cntr, shell, l)
##                cnt += 1
##            shell += 1
##        # Previous center is now center
##        pcntr = cntr
##    # Chop off what we don't need
##    df = pd.DataFrame(df[:cnt])
##    # Now to deduplicate identical basis sets
##    # Gaussian prints out every single atomic basis set
##    df, setmap = _dedup(df)
##    return df, setmap
##
##
##_csv_args = {'delim_whitespace': True, 'header': None}
### Atom flags
##_regeom01 = 'Input orientation'
##_regeom02 = 'Standard orientation'
### Orbital flags
##_reorb01 = '(?=Alpha|Beta).*(?=occ|virt)'
##_reorb02 = 'Orbital symmetries'
##_orbslice = [slice(10 * i, 10 * i + 9) for i in range(5)]
##_symrep = {'Occupied': '', 'Virtual': '', 'Alpha Orbitals:': '',
##           'Beta  Orbitals:': '', '\(': '', '\)': ''}
##_resympat = re.compile('|'.join(_symrep.keys()))
##_symrep['('] = ''
##_symrep[')'] = ''
### MOMatrix flags
##_remomat01 = r'pop.*(?=full|no)'
##_remomat02 = 'Orbital Coefficients'
### Basis flags
##_rebas01 = r'gfinput'
##_rebas02 = 'basis functions,'
##_rebas03 = ' ****'
##_rebas04 = 'General basis'
##_basrep = {'D 0': 'D0', 'F 0': 'F0',
##           'G 0': 'G0', 'H 0': 'H0', 'I 0': 'I0'}
##_rebaspat = re.compile('|'.join(_basrep.keys()))
### Frame flags
##_retoten = 'SCF Done:'
##_realphaelec = 'alpha electrons'
##_reelecstate = 'The electronic state'
### Frequency flags
##_refreq = 'Freq'
### TDDFT flags
##_retddft = 'TD'
##_reexcst = 'Excited State'
### Triangular matrices -- One electron integrals
##_reovl01 = '*** Overlap ***'
##_reixn = 'IX=    {}'
##
##class Fchk(Editor):
##
##    def _intme(self, fitem):
##        """Helper gets an integer of interest."""
##        return int(self[fitem[0]].split()[-1])
##
##    def _dfme(self, fitem, dim):
##        """Helper gets an array of interest."""
##        start = fitem[0] + 1
##        col = min(len(self[start].split()), dim)
##        stop = np.ceil(start + dim / col).astype(np.int64)
##        return self.pandas_dataframe(start, stop, col).stack().values
##
##    def parse_atom(self):
##        # Find line numbers of interest
##        found = self.find(_renat, _reznum, _rezeff, _reposition,
##                          stop=100, keys_only=True)
##        # Number of atoms in current geometry
##        nat = self._intme(found[_renat])
##        # Atom identifiers
##        znums = self._dfme(found[_reznum], nat)
##        # Atomic symbols
##        symbols = list(map(lambda x: z_to_symbol[x], znums))
##        # Z effective if ECPs are used
##        zeffs = self._dfme(found[_rezeff], nat).astype(np.int64)
##        # Atomic positions
##        pos = self._dfme(found[_reposition], nat * 3).reshape(nat, 3)
##        frame = np.zeros(len(symbols), dtype=np.int64)
##        self.atom = pd.DataFrame.from_dict({'symbol': symbols, 'Zeff': zeffs,
##                                            'frame': frame, 'x': pos[:,0],
##                                            'y': pos[:,1], 'z': pos[:,2],
##                                            'set': range(1, len(symbols) + 1)})
##
##    def parse_basis_set(self):
##        found = self.find(_rebasdim, _reshelltype, _reprimpershell,
##                          _reshelltoatom, _reprimexp, _recontcoef,
##                          _repcontcoef, keys_only=True)
##        # Number of basis functions
##        nbas = self._intme(found[_rebasdim])
##        # Number of 'shell to atom' mappings
##        dim1 = self._intme(found[_reshelltype])
##        # Number of primitive exponents
##        dim2 = self._intme(found[_reprimexp])
##        # Handle cartesian vs. spherical here
##        # only spherical for now
##        shelltypes = self._dfme(found[_reshelltype], dim1).astype(np.int64)
##        primpershell = self._dfme(found[_reprimpershell], dim1).astype(np.int64)
##        shelltoatom = self._dfme(found[_reshelltoatom], dim1).astype(np.int64)
##        primexps = self._dfme(found[_reprimexp], dim2)
##        contcoefs = self._dfme(found[_recontcoef], dim2)
##        if found[_repcontcoef]: pcontcoefs = self._dfme(found[_repcontcoef], dim2)
##        # Keep track of some things
##        ptr, prevatom, shell, sp = 0, 0, 0, False
##        # Temporary storage of basis set data
##        ddict = {'d': [], 'alpha': [], 'shell': [],
##                 'L': [], 'center': []}
##        for atom, nprim, shelltype in zip(shelltoatom, primpershell, shelltypes):
##            if atom != prevatom:
##                prevatom, shell = atom, 0
##            # Collect the data for this basis set
##            if shelltype == -1:
##                shelltype, sp = 0, True
##            step = ptr + nprim
##            ddict['d'] += contcoefs[ptr:step].tolist()
##            ddict['alpha'] += primexps[ptr:step].tolist()
##            ddict['center'] += [atom] * nprim
##            ddict['shell'] += [shell] * nprim
##            ddict['L'] += [np.abs(shelltype)] * nprim
##            if sp:
##                shell += 1
##                ddict['d'] += pcontcoefs[ptr:step].tolist()
##                ddict['alpha'] += primexps[ptr:step].tolist()
##                ddict['center'] += [atom] * nprim
##                ddict['shell'] += [shell] * nprim
##                ddict['L'] += [1] * nprim
##            ptr += nprim
##            shell += 1
##            sp = False
##        sets, setmap = _dedup(pd.DataFrame.from_dict(ddict))
##        self.basis_set = sets
##        self.atom['set'] = self.atom['set'].map(setmap)
##
##    def parse_orbital(self):
##        found = self.find(_realphaen)
##        pass
##
##    def parse_basis_set_order(self):
##        # Unique basis sets
##        sets = self.basis_set.groupby('set')
##        data = []
##        # Gaussian orders basis functions strangely
##        # Will likely need an additional mapping for cartesian
##        lmap = {0: [0], 1: [1, -1, 0],
##                2: [0, 1, -1, 2, -2],
##                3: [0, 1, -1, 2, -2, 3, -3],
##                4: [0, 1, -1, 2, -2, 3, -3, 4, -4],
##                5: [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]}
##        # What was tag column for in basis set order?
##        key = 'tag' if 'tag' in self.atom.columns else 'symbol'
##        # Iterate over atoms
##        for cent, bset, tag in zip(self.atom.index.values, self.atom['set'], self.atom[key]):
##            seht = sets.get_group(bset).groupby('shell')
##            # Iterate over basis set
##            for shell, grp in seht:
##                L = grp['L'].values[0]
##                # Iterate over m_l values
##                for ml in lmap[L]:
##                    data.append([cent, tag, L, ml, shell, 0])
##        columns = ('center', 'tag', 'L', 'ml', 'shell', 'frame')
##        self.basis_set_order = pd.DataFrame(data, columns=columns)
##
##    def parse_momatrix(self):
##        found = self.find(_rebasdim, _reindepdim, _reamomatrix, _rebmomatrix,
##                          keys_only=True)
##        # Again number of basis functions
##        nbas = self._intme(found[_rebasdim])
##        try:
##            ninp = self._intme(found[_reindepdim])
##        except IndexError:
##            ninp = nbas
##        ncoef = self._intme(found[_reamomatrix])
##        if nbas * ninp != ncoef:
##            raise Exception('Dimensions are inconsistent.')
##            return
##        # Alpha or closed shell MO coefficients
##        coefs = self._dfme(found[_reamomatrix], ncoef)
##        # Beta MO coefficients if they exist
##        bcoefs = self._dfme(found[_rebmomatrix], ncoef) \
##                 if found[_rebmomatrix] else None
##        # Indexing
##        chis = np.tile(range(nbas), ninp)
##        orbitals = np.repeat(range(ninp), nbas)
##        frame = np.zeros(ncoef, dtype=np.int64)
##        self.momatrix = pd.DataFrame.from_dict({'chi': chis, 'orbital': orbitals,
##                                                'coef': coefs, 'frame': frame})
##        if bcoefs is not None:
##            self.momatrix['coef1'] = bcoefs
##
##    def __init__(self, *args, **kwargs):
##        super().__init__(*args, **kwargs)
##
##
##def _dedup(sets):
##    unique, setmap, cnt = [], {}, 0
##    sets = sets.groupby('center')
##    chk = ['alpha', 'd']
##    for center, seht in sets:
##        for i, other in enumerate(unique):
##            if other.shape != seht.shape: continue
##            if np.allclose(other[chk], seht[chk]):
##                setmap[center] = i
##                break
##        else:
##            unique.append(seht)
##            setmap[center] = cnt
##            cnt += 1
##    sets = pd.concat(unique).reset_index(drop=True)
##    sets.rename(columns={'center': 'set'}, inplace=True)
##    sets['set'] = sets['set'].map(setmap)
##    sets['frame'] = 0
##    return sets, setmap
##
### Atom regex
##_renat = 'Number of atoms'
##_reznum = 'Atomic numbers'
##_rezeff = 'Nuclear charges'
##_reposition = 'Current cartesian coordinates'
##
### Basis set regex
##_rebasdim = 'Number of basis functions'
##_recontdim = 'Number of contracted shells'
##_reprimdim = 'Number of primitive shells'
##_reshelltype = 'Shell types'
##_reprimpershell = 'Number of primitives per shell'
##_reshelltoatom = 'Shell to atom map'
##_reprimexp = 'Primitive exponents'
##_recontcoef = 'Contraction coefficients'
##_repcontcoef = 'P(S=P) Contraction coefficients'
##
### MOMatrix regex
### also uses _rebasdim
##_reindepdim = 'Number of independant functions'
##_realphaen = 'Alpha Orbital Energies'
##_reamomatrix = 'Alpha MO coefficients'
##_rebmomatrix = 'Beta MO coefficients'
#=======
#import re
#import numpy as np
#import pandas as pd
#from io import StringIO
#
#from exatomic import Length
#from .editor import Editor
#from exa.relational.isotope import z_to_symbol
#from exatomic import Energy
#from exatomic.frame import compute_frame_from_atom
#from exatomic.basis import BasisSet
#from exatomic.orbital import Orbital
#from exatomic.algorithms.basis import lmap, lorder
#
#z_to_symbol = z_to_symbol()
#
#from numba import jit, int64
#@jit(nopython=True, cache=True)
#def _triangular_indices(ncol, nbas):
#    dim = nbas * (nbas + 1) // 2
#    idx = np.empty((dim, 3), dtype=np.int64)
#    cnt = 0
#    for i in range(ncol):
#        for j in range(i, nbas, ncol):
#            for k in range(j, nbas):
#                idx[cnt,0] = j
#                idx[cnt,1] = k
#                idx[cnt,2] = 0
#                cnt += 1
#    return idx
#
#class Output(Editor):
#
#    def _parse_triangular_matrix(self, regex, column='coef', values_only=False):
#        found = self.find_next(_rebas01, keys_only=True)
#        nbas = int(self[found].split()[0])
#        found = self.find_next(regex, keys_only=True)
#        if not found: return
#        ncol = len(self[found + 1].split())
#        start = found + 2
#        rmdr = nbas % ncol
#        skips = np.array(list(reversed(range(rmdr, nbas + max(1, rmdr), ncol))))
#        skips = np.cumsum(skips) + np.arange(len(skips))
#        stop = start + skips[-1]
#        matrix = self.pandas_dataframe(start, stop, ncol + 1,
#                                       index_col=0, skiprows=skips,
#                                       ).unstack().dropna().apply(
#                                       lambda x: x.replace('D', 'E')
#                                       ).astype(np.float64).values
#        if values_only: return matrix
#        idxs = _triangular_indices(ncol, nbas)
#        return pd.DataFrame.from_dict({'chi0': idxs[:,0],
#                                       'chi1': idxs[:,1],
#                                      'frame': idxs[:,2],
#                                       column: matrix})
#
#    def parse_atom(self):
#        # Find our data
#        found = self.find(_regeom01, _regeom02, keys_only=True)
#        # Check if nosymm was specified
#        key = _regeom02 if found[_regeom02] else _regeom01
#        starts = np.array(found[key]) + 5
#        # Prints converged geometry twice but only need it once
#        starts = starts[:-1] if len(starts) > 1 else starts
#        stop = starts[0]
#        # Find where the data stops
#        while '-------' not in self[stop]: stop += 1
#        # But it should be same sized array each time
#        stops = starts + (stop - starts[0])
#        dfs = []
#        # Iterate over frames
#        for i, (start, stop) in enumerate(zip(starts, stops)):
#            atom = self.pandas_dataframe(start, stop, 6)
#            atom['frame'] = i
#            dfs.append(atom)
#        atom = pd.concat(dfs).reset_index(drop=True)
#        # Drop the column of atomic type (whatever that is)
#        atom.drop([2], axis=1, inplace=True)
#        # Name the data
#        atom.columns = ['set', 'Z', 'x', 'y', 'z', 'frame']
#        # Zero-based indexing
#        atom['set'] -= 1
#        # Convert to atomic units
#        atom['x'] *= Length['A', 'au']
#        atom['y'] *= Length['A', 'au']
#        atom['z'] *= Length['A', 'au']
#        # Map atomic symbols onto Z numbers
#        atom['symbol'] = atom['Z'].map(z_to_symbol)
#        self.atom = atom
#
#    def parse_basis_set(self):
#        # Find the basis set
#        found = self.regex(_rebas02, _rebas03, keys_only=True)
#        if not found[_rebas02]: return
#        start = stop = found[_rebas02][0] + 1
#        while self[stop].strip(): stop += 1
#        # Raw data
#        df = self.pandas_dataframe(start, stop, 4)
#        def _padx(srs): return [0] + srs.tolist() + [df.shape[0]]
#        # Get some indices for appropriate columns
#        setdx = _padx(df[0][df[0] == '****'].index)
#        shldx = _padx(df[3][~np.isnan(df[3])].index)
#        lindx = df[0][df[0].str.lower().isin(lorder + ['sp'])]
#        # Populate the df
#        df['L'] = lindx.str.lower().map(lmap)
#        df['L'] = df['L'].fillna(method='ffill').fillna(
#                                 method='bfill').astype(np.int64)
#        df['center'] = np.concatenate([np.repeat(i, stop - start)
#                       for i, (start, stop) in enumerate(zip(setdx, setdx[1:]))])
#        df['shell'] = np.concatenate([np.repeat(i-1, stop - start)
#                      for i, (start, stop) in enumerate(zip(shldx, shldx[1:]))])
#        # Complicated way to get shells but it is flat
#        maxshl = df.groupby('center').apply(lambda x: x.shell.max() + 1)
#        maxshl.index += 1
#        maxshl[0] = 0
#        df['shell'] = df['shell'] - df['center'].map(maxshl)
#        # Drop all the garbage
#        todrop = setdx[:-1] + [i+1 for i in setdx[:-2]] + lindx.index.tolist()
#        df.drop(todrop, inplace=True)
#        # Keep cleaning
#        if df[0].dtype == 'object':
#            df[0] = df[0].str.replace('D', 'E').astype(np.float64)
#        if df[1].dtype == 'object':
#            df[1] = df[1].str.replace('D', 'E').astype(np.float64)
#        try: sp = np.isnan(df[2]).sum() == df.shape[0]
#        except TypeError:
#            df[2] = df[2].str.replace('D', 'E').astype(np.float64)
#            sp = True
#        # Deduplicate basis sets and expand 'SP' shells if present
#        df, setmap = _dedup(df, sp=sp)
#        spherical = '5D' in self[found[_rebas03][0]]
#        self.basis_set = BasisSet(df, spherical=spherical)
#        self.atom['set'] = self.atom['set'].map(setmap)
#
#
#    def parse_orbital(self):
#        # Find where our data is
#        found = self.regex(_reorb01, _reorb02, _rebas01, _realphaelec)
#        # If no orbital energies, quit
#        if not found[_reorb01]: return
#        # Basis dimension
#        nbas = int(found[_rebas01][0][1].split()[0])
#        # Check if open shell
#        os = any(('Beta' in ln for lno, ln in found[_reorb01]))
#        occ = 1 if os else 2
#        # Find number of electrons
#        ae, x, x, be, x, x = found[_realphaelec][0][1].split()
#        ae, be = int(ae), int(be)
#        # Get orbital energies
#        ens = '\n'.join([ln.split('--')[1][1:] for i, ln in found[_reorb01]])
#        ens = pd.read_fwf(StringIO(ens), header=None,
#                          widths=np.repeat(10, 5)).stack().values
#        # Other arrays
#        orbital = Orbital.from_energies(ens, nbas, ae, be)
#        # Symmetry labels
#        if found[_reorb02]:
#            # Gaussian seems to print out a lot of these blocks
#            # maybe a better way to deal with this
#            allsyms = []
#            match = ['(', 'Orbitals']
#            for i, (start, ln) in enumerate(found[_reorb02]):
#                # Find the start, stop indices for each block
#                while match[0] not in self[start]: start += 1
#                stop = start + 1
#                while any((i in self[stop] for i in match)): stop += 1
#                # Clean up the text block so it is just symmetries
#                syms = _resympat.sub(lambda m: _symrep[m.group(0)],
#                                     ' '.join([i.strip() for i in
#                                     self[start:stop]])).split()
#                # cat the syms for each block together
#                allsyms += syms
#            # Add it to our dataframe
#            orbital['symmetry'] = allsyms[-orbital.shape[0]:]
#        self.orbital = orbital
#
#
#    def parse_momatrix(self):
#        """
#        Parses the MO matrix if asked for in the input.
#
#        Note:
#            Requires specification of pop(full) or pop(no) or the like.
#        """
#        if hasattr(self, '_momatrix'): return
#        # Check if a full MO matrix was specified in the input
#        check = self.regex(_remomat01, stop=1000, flags=re.IGNORECASE)
#        if not check: return
#        # Find approximately where our data is
#        found = self.find(_remomat02, _rebas01)
#        # Get some dimensions
#        ndim = len(found[_remomat02])
#        # If something goes wrong
#        if not ndim: return
#        nbas = int(found[_rebas01][0][1].split()[0])
#        nblocks = np.int64(np.ceil(nbas / 5))
#        # Allocate a big ol' array
#        coefs = np.empty((nbas ** 2, ndim), dtype=np.float64)
#        # Dynamic column generation hasn't been worked out yet
#        colnames = ['coef'] + ['coef' + str(i) for i in range(1, ndim)]
#        # Iterate over where the data was found
#        # c counts the column in the resulting momatrix table
#        finds = ['Eigenvalues', 'EIGENVALUES']
#        for c, (lno, ln) in enumerate(found[_remomat02]):
#            while not any((find in self[lno] for find in finds)): lno += 1
#            start = lno + 1
#            stop = start + nbas
#            # The basis set order is printed with every chunk of eigenvectors
#            if c == 0: self.basis_set_order = _basis_set_order(self[start:stop])
#            # Some fudge factors due to extra lines being printed
#            space = start - lno - 1
#            fnbas = nbas + space
#            span = start + fnbas * nblocks
#            # Finally get where our chunks are
#            starts = np.arange(start, span, fnbas)
#            stops = np.arange(stop, span, fnbas)
#            stride = 0
#            # b counts the blocks of eigenvectors per column in momatrix
#            for b, (start, stop) in enumerate(zip(starts, stops)):
#                # Number of eigenvectors in this block
#                ncol = len(self[start][20:].split())
#                _csv_args['names'] = range(ncol)
#                # Massage the text so that we can read csv
#                block = '\n'.join([ln[20:] for ln in self[start:stop]])
#                block = _rebaspat.sub(lambda m: _basrep[m.group(0)], block)
#                # Enplacen the resultant unstacked values
#                coefs[stride:stride + nbas * ncol, c] = pd.read_csv(
#                    StringIO(block), **_csv_args).unstack().values
#                stride += nbas * ncol
#        # Index chi, phi
#        chis = np.tile(range(nbas), nbas)
#        orbs = np.repeat(range(nbas), nbas)
#        momatrix = pd.DataFrame(coefs, columns=colnames)
#        momatrix['chi'] = chis
#        momatrix['orbital'] = orbs
#        # Frame not really implemented for momatrix
#        momatrix['frame'] = 0
#        self.momatrix = momatrix
#
#    def parse_basis_set_order(self):
#        if hasattr(self, '_basis_set_order'): return
#        self.parse_momatrix()
#
#
#    def parse_frame(self):
#        # Get the default frame from the atom table
#        self.frame = compute_frame_from_atom(self.atom)
#        # Find our data
#        found = self.find(_retoten, _realphaelec, _reelecstate)
#        # Extract just the total SCF energies
#        ens = [float(ln.split()[4]) for lno, ln in found[_retoten]]
#        # If 'SCF Done' prints out more times than frames
#        try:
#            ens = ens if len(self.frame) == len(ens) else ens[-len(self.frame):]
#            self.frame['E_tot'] = ens
#        except:
#            pass
#        # We will assume number of electrons doesn't change per frame
#        ae, x, x, be, x, x = found[_realphaelec][0][1].split()
#        self.frame['N_e'] = int(ae) + int(be)
#        self.frame['N_a'] = int(ae)
#        self.frame['N_b'] = int(be)
#        # Try to get the electronic state but don't try too hard
#        try:
#            states = []
#            for lno, ln in found[_reelecstate]:
#                if 'initial' in ln: continue
#                states.append(ln.split()[4].replace('.', ''))
#            self.frame['state'] = states
#        except (IndexError, ValueError):
#            pass
#
#
#    def parse_excitation(self):
#        chk = self.find(_retddft, stop=1000, keys_only=True)
#        if not chk: return
#        # Find the data
#        found = self.find(_reexcst)
#        keeps, maps, summ = [], [] ,[]
#        for i, (lno, ln) in enumerate(found):
#            summ.append(ln)
#            lno += 1
#            while '->' in self[lno]:
#                keeps.append(lno)
#                maps.append(i)
#                lno += 1
#        cols = [0, 1, 2, 'kind', 'eV', 3, 'nm', 4, 'osc', 's2']
#        summ = pd.read_csv(StringIO('\n'.join([ln for lno, ln in found])),
#                           delim_whitespace=True, header=None, names=cols,
#                           usecols=[c for c in cols if type(c) == str])
#        summ['s2'] = summ['s2'].str[7:].astype(np.float64)
#        summ['osc'] = summ['osc'].str[2:].astype(np.float64)
#        cols = ['occ', 0, 'virt', 'cont']
#        conts = pd.read_csv(StringIO('\n'.join([self[i] for i in keeps])),
#                            delim_whitespace=True, header=None, names=cols,
#                            usecols=[c for c in cols if type(c) == str])
#        conts['map'] = maps
#        for col in summ.columns:
#            conts[col] = conts['map'].map(summ[col])
#        conts['energy'] = conts['eV'] * Energy['eV', 'Ha']
#        conts['frame'] = conts['group'] = 0
#        self.excitation = conts
#
#
#    def parse_frequency(self):
#        found = self.regex(_refreq, stop=1000, flags=re.IGNORECASE)
#        # Don't need the input deck or 2 from the summary at the end
#        found = self.find(_refreq)[1:-2]
#        if not found: return
#        # Total lines per block minus the unnecessary ones
#        span = found[1][0] - found[0][0] - 7
#        dfs, fdx = [], 0
#        # Iterate over what we found
#        for lno, ln in found:
#            # Get the frequencies first
#            freqs = ln[15:].split()
#            nfreqs = len(freqs)
#            # Get just the atom displacement vectors
#            start = lno + 5
#            stop = start + span
#            cols = range(2 + 3 * nfreqs)
#            df = self.pandas_dataframe(start, stop, ncol=cols)
#            # Split up the df and unstack it
#            slices = [list(range(2 + i, 2 + 3 * nfreqs, 3)) for i in range(nfreqs)]
#            dx, dy, dz = [df[i].unstack().values for i in slices]
#            # Generate the appropriate dimensions of other columns
#            labels = np.tile(df[0].values, nfreqs)
#            zs = np.tile(df[1].values, nfreqs)
#            freqdxs = np.repeat(range(fdx, fdx + nfreqs), df.shape[0])
#            freqs = np.repeat(freqs, df.shape[0])
#            fdx += nfreqs
#            # Put it all together
#            stacked = pd.DataFrame.from_dict({'Z': zs, 'label': labels,
#                                    'dx': dx, 'dy': dy, 'dz': dz,
#                                    'frequency': freqs, 'freqdx': freqdxs})
#            stacked['symbol'] = stacked['Z'].map(z_to_symbol)
#            dfs.append(stacked)
#        # Now put all our frequencies together
#        frequency = pd.concat(dfs).reset_index(drop=True)
#        # Pretty sure displacements are in cartesian angstroms
#        # TODO: verify with an external program that vibrational
#        #       modes look the same as the ones generated with
#        #       this methodology.
#        frequency['dx'] *= Length['A', 'au']
#        frequency['dy'] *= Length['A', 'au']
#        frequency['dz'] *= Length['A', 'au']
#        # Frame not really implemented here either
#        frequency['frame'] = 0
#        self.frequency = frequency
#
#
#    def parse_overlap(self):
#        overlap = self._parse_triangular_matrix(_reovl01, 'coef')
#        if overlap is not None: self.overlap = overlap
#
#    def parse_multipole(self):
#        mltpl = self._parse_triangular_matrix(_reixn.format(1), 'ix1')
#        if mltpl is not None:
#            mltpl['ix2'] = self._parse_triangular_matrix(_reixn.format(2), 'ix2', True)
#            mltpl['ix3'] = self._parse_triangular_matrix(_reixn.format(3), 'ix3', True)
#            self.multipole = mltpl
#
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#
#
#def _basis_set_order(chunk):
#    # Gaussian only prints the atom center
#    # and label once for all basis functions
#    first = len(chunk[0]) - len(chunk[0].lstrip(' ')) + 1
#    df = pd.read_fwf(StringIO('\n'.join(chunk)),
#                     widths=[first, 4, 3, 2, 4], header=None)
#    df[1].fillna(method='ffill', inplace=True)
#    df[1] = df[1].astype(np.int64) - 1
#    df[2].fillna(method='ffill', inplace=True)
#    df.rename(columns={1: 'center', 3: 'N', 4: 'ang'}, inplace=True)
#    df['N'] = df['N'].astype(np.int64) - 1
#    cart = 'XX' in df['ang'].values
#    if cart:
#        df[['L', 'l', 'm', 'n']] = df['ang'].map({'S': [0, 0, 0, 0],
#                'XX': [2, 2, 0, 0], 'XY': [2, 1, 1, 0], 'XZ': [2, 1, 0, 1],
#                'YY': [2, 0, 2, 0], 'YZ': [2, 0, 1, 1], 'ZZ': [2, 0, 0, 2],
#                'PX': [1, 1, 0, 0], 'PY': [1, 0, 1, 0], 'PZ': [1, 0, 0, 1],
#                }).apply(tuple).apply(pd.Series)
#    else:
#        df['L'] = df['ang'].str[:1].str.lower().map(lmap).astype(np.int64)
#        df['ml'] = df['ang'].str[1:]
#        df['ml'].update(df['ml'].map({'': 0, 'X': 1, 'Y': -1, 'Z': 0}))
#        df['ml'] = df['ml'].astype(np.int64)
#    shl, pcen, pl, pn, shfns = -1, -1, -1, -1, []
#    for cen, n, l in zip(df['center'], df['N'], df['L']):
#        if not pcen == cen: shl = -1
#        if (not pl == l) or (not pn == n) or (not pcen == cen): shl += 1
#        shfns.append(shl)
#        pcen, pl, pn = cen, l, n
#    df['shell'] = shfns
#    df.drop([0, 2, 'N', 'ang'], axis=1, inplace=True)
#    df['frame'] = 0
#    return df
#
#
#_csv_args = {'delim_whitespace': True, 'header': None}
## Atom flags
#_regeom01 = 'Input orientation'
#_regeom02 = 'Standard orientation'
## Orbital flags
#_reorb01 = '(?=Alpha|Beta).*(?=occ|virt)'
#_reorb02 = 'Orbital symmetries'
#_orbslice = [slice(10 * i, 10 * i + 9) for i in range(5)]
#_symrep = {'Occupied': '', 'Virtual': '', 'Alpha Orbitals:': '',
#           'Beta  Orbitals:': '', '\(': '', '\)': ''}
#_resympat = re.compile('|'.join(_symrep.keys()))
#_symrep['('] = ''
#_symrep[')'] = ''
## MOMatrix flags
#_remomat01 = r'pop.*(?=full|no)'
#_remomat02 = 'Orbital Coefficients'
## Basis flags
#_rebas01 = r'basis functions,'
#_rebas02 = 'AO basis set in the form of general basis input'
#_rebas03 = ' (Standard|General) basis'
#_basrep = {'D 0': 'D0', 'F 0': 'F0',
#           'G 0': 'G0', 'H 0': 'H0', 'I 0': 'I0'}
#_rebaspat = re.compile('|'.join(_basrep.keys()))
## Frame flags
#_retoten = 'SCF Done:'
#_realphaelec = 'alpha electrons'
#_reelecstate = 'The electronic state'
## Frequency flags
#_refreq = 'Freq'
## TDDFT flags
#_retddft = 'TD'
#_reexcst = 'Excited State'
## Triangular matrices -- One electron integrals
#_reovl01 = '*** Overlap ***'
#_reixn = 'IX=    {}'
#
#class Fchk(Editor):
#
#    def _intme(self, fitem, idx=0):
#        """Helper gets an integer of interest."""
#        return int(self[fitem[idx]].split()[-1])
#
#    def _dfme(self, fitem, dim, idx=0):
#        """Helper gets an array of interest."""
#        start = fitem[idx] + 1
#        col = min(len(self[start].split()), dim)
#        stop = np.ceil(start + dim / col).astype(np.int64)
#        return self.pandas_dataframe(start, stop, col).stack().values
#
#    def parse_atom(self):
#        # Find line numbers of interest
#        found = self.find(_renat, _reznum, _rezeff, _reposition,
#                          stop=100, keys_only=True)
#        # Number of atoms in current geometry
#        nat = self._intme(found[_renat])
#        # Atom identifiers
#        znums = self._dfme(found[_reznum], nat)
#        # Atomic symbols
#        symbols = list(map(lambda x: z_to_symbol[x], znums))
#        # Z effective if ECPs are used
#        zeffs = self._dfme(found[_rezeff], nat).astype(np.int64)
#        # Atomic positions
#        pos = self._dfme(found[_reposition], nat * 3).reshape(nat, 3)
#        frame = np.zeros(len(symbols), dtype=np.int64)
#        self.atom = pd.DataFrame.from_dict({'symbol': symbols, 'Zeff': zeffs,
#                                            'frame': frame, 'x': pos[:,0],
#                                            'y': pos[:,1], 'z': pos[:,2],
#                                            'set': range(1, len(symbols) + 1)})
#
#    def parse_basis_set(self):
#        found = self.find(_rebasdim, _reshelltype, _reprimpershell,
#                          _reshelltoatom, _reprimexp, _recontcoef,
#                          _repcontcoef, keys_only=True)
#        # Number of basis functions
#        nbas = self._intme(found[_rebasdim])
#        # Number of 'shell to atom' mappings
#        dim1 = self._intme(found[_reshelltype])
#        # Number of primitive exponents
#        dim2 = self._intme(found[_reprimexp])
#        # Handle cartesian vs. spherical here
#        # only spherical for now
#        shelltypes = self._dfme(found[_reshelltype], dim1).astype(np.int64)
#        primpershell = self._dfme(found[_reprimpershell], dim1).astype(np.int64)
#        shelltoatom = self._dfme(found[_reshelltoatom], dim1).astype(np.int64)
#        primexps = self._dfme(found[_reprimexp], dim2)
#        contcoefs = self._dfme(found[_recontcoef], dim2)
#        if found[_repcontcoef]: pcontcoefs = self._dfme(found[_repcontcoef], dim2)
#        # Keep track of some things
#        ptr, prevatom, shell, sp = 0, 0, 0, False
#        # Temporary storage of basis set data
#        ddict = {1: [], 0: [], 'shell': [],
#                 'L': [], 'center': []}
#        for atom, nprim, shelltype in zip(shelltoatom, primpershell, shelltypes):
#            if atom != prevatom:
#                prevatom, shell = atom, 0
#            # Collect the data for this basis set
#            if shelltype == -1:
#                shelltype, sp = 0, True
#            step = ptr + nprim
#            ddict[1] += contcoefs[ptr:step].tolist()
#            ddict[0] += primexps[ptr:step].tolist()
#            ddict['center'] += [atom] * nprim
#            ddict['shell'] += [shell] * nprim
#            ddict['L'] += [np.abs(shelltype)] * nprim
#            if sp:
#                shell += 1
#                ddict[1] += pcontcoefs[ptr:step].tolist()
#                ddict[0] += primexps[ptr:step].tolist()
#                ddict['center'] += [atom] * nprim
#                ddict['shell'] += [shell] * nprim
#                ddict['L'] += [1] * nprim
#            ptr += nprim
#            shell += 1
#            sp = False
#        sets, setmap = _dedup(pd.DataFrame.from_dict(ddict))
#        self.basis_set = sets
#        self.atom['set'] = self.atom['set'].map(setmap)
#
#    def parse_basis_set_order(self):
#        # Unique basis sets
#        sets = self.basis_set.groupby('set')
#        data = []
#        # Gaussian orders basis functions strangely
#        # Will likely need an additional mapping for cartesian
#        lamp = {0: [0], 1: [1, -1, 0],
#                2: [0, 1, -1, 2, -2],
#                3: [0, 1, -1, 2, -2, 3, -3],
#                4: [0, 1, -1, 2, -2, 3, -3, 4, -4],
#                5: [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]}
#        # What was tag column for in basis set order?
#        key = 'tag' if 'tag' in self.atom.columns else 'symbol'
#        # Iterate over atoms
#        for cent, bset, tag in zip(self.atom.index.values, self.atom['set'], self.atom[key]):
#            seht = sets.get_group(bset).groupby('shell')
#            # Iterate over basis set
#            for shell, grp in seht:
#                L = grp['L'].values[0]
#                # Iterate over m_l values
#                for ml in lamp[L]:
#                    data.append([cent, tag, L, ml, shell, 0])
#        columns = ('center', 'tag', 'L', 'ml', 'shell', 'frame')
#        self.basis_set_order = pd.DataFrame(data, columns=columns)
#
#    def parse_momatrix(self):
#        found = self.find(_rebasdim, _reindepdim, _reamomatrix, _rebmomatrix,
#                          keys_only=True)
#        # Again number of basis functions
#        nbas = self._intme(found[_rebasdim])
#        try:
#            ninp = self._intme(found[_reindepdim])
#        except IndexError:
#            ninp = nbas
#        ncoef = self._intme(found[_reamomatrix])
#        # Alpha or closed shell MO coefficients
#        coefs = self._dfme(found[_reamomatrix], ncoef)
#        # Beta MO coefficients if they exist
#        bcoefs = self._dfme(found[_rebmomatrix], ncoef) \
#                 if found[_rebmomatrix] else None
#        # Indexing
#        chis = np.tile(range(nbas), ninp)
#        orbitals = np.repeat(range(ninp), nbas)
#        frame = np.zeros(ncoef, dtype=np.int64)
#        self.momatrix = pd.DataFrame.from_dict({'chi': chis, 'orbital': orbitals,
#                                                'coef': coefs, 'frame': frame})
#        if bcoefs is not None:
#            self.momatrix['coef1'] = bcoefs
#
#
#    def parse_orbital(self):
#        found = self.regex(_reorben, _reorboc, keys_only=True)
#        ae = self._intme(found[_reorboc], idx=0)
#        be = self._intme(found[_reorboc], idx=1)
#        nbas = self._intme(found[_reorben])
#        ens = np.concatenate([self._dfme(start, nbas, idx=i)
#                              for i, start in enumerate(found[_reorben])])
#        self.orbital = Orbital.from_energies(ens, nbas, ae, be)
#
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#
#def _dedup(sets, sp=False):
#    unique, setmap, cnt = [], {}, 0
#    sets = sets.groupby('center')
#    chk = [0, 1]
#    for center, seht in sets:
#        for i, other in enumerate(unique):
#            if other.shape != seht.shape: continue
#            if np.allclose(other[chk], seht[chk]):
#                setmap[center] = i
#                break
#        else:
#            unique.append(seht)
#            setmap[center] = cnt
#            cnt += 1
#    if sp: unique = _expand_sp(unique)
#    sets = pd.concat(unique).reset_index(drop=True)
#    try: sets.drop([2, 3], axis=1, inplace=True)
#    except ValueError: pass
#    sets.rename(columns={'center': 'set', 0: 'alpha', 1: 'd'}, inplace=True)
#    sets['set'] = sets['set'].map(setmap)
#    sets['frame'] = 0
#    return sets, setmap
#
#def _expand_sp(unique):
#    expand = []
#    for seht in unique:
#        if np.isnan(seht[2]).sum() == seht.shape[0]:
#            expand.append(seht)
#            continue
#        sps = seht[2][~np.isnan(seht[2])].index
#        shls = len(seht.ix[sps]['shell'].unique())
#        dupl = seht.ix[sps[0]:sps[-1]].copy()
#        dupl[1] = dupl[2]
#        dupl['L'] = 1
#        dupl['shell'] += shls
#        last = seht.ix[sps[-1] + 1:].copy()
#        last['shell'] += shls
#        expand.append(pd.concat([seht.ix[:sps[0] - 1],
#                                 seht.ix[sps[0]:sps[-1]],
#                                 dupl, last]))
#    return expand
#
## Atom regex
#_renat = 'Number of atoms'
#_reznum = 'Atomic numbers'
#_rezeff = 'Nuclear charges'
#_reposition = 'Current cartesian coordinates'
#
## Basis set regex
#_rebasdim = 'Number of basis functions'
#_recontdim = 'Number of contracted shells'
#_reprimdim = 'Number of primitive shells'
#_reshelltype = 'Shell types'
#_reprimpershell = 'Number of primitives per shell'
#_reshelltoatom = 'Shell to atom map'
#_reprimexp = 'Primitive exponents'
#_recontcoef = 'Contraction coefficients'
#_repcontcoef = 'P(S=P) Contraction coefficients'
#
## MOMatrix regex
## also uses _rebasdim
#_reindepdim = 'Number of independant functions'
#_realphaen = 'Alpha Orbital Energies'
#_reamomatrix = 'Alpha MO coefficients'
#_rebmomatrix = 'Beta MO coefficients'
#
## Orbital regex
#_reorboc = 'Number of .*electrons'
#_reorben = 'Orbital Energies'
#>>>>>>> org/master
