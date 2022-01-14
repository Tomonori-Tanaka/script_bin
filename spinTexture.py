import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import math

def scriptFilter(args):
    if args.quiet is False:
        print("Filtering...")
        print("Input        :", args.inFile)
        print("Output       :", args.outFile)

    kpoints = []
    energies = []
    tot = []
    infile = args.inFile
    with open(infile, mode='r', encoding='utf-8') as f:
        for line in f:
            if line.find("k-points") >= 0:
                # of k-points:  338     # of bands: 250     # of ions:  35
                numband = int(line.split()[7])
                continue
            elif line.find("k-point") >= 0:
                '''
                    sometimes k-point format is
                    k-point    1 :   -0.50000000-0.50000000 0.00000000     weight = 0.01000000
                    minus stuck to values
                    This is terrible format!!!
                    we replace "-" to " -"
                '''
                line = line.split(" ", maxsplit=2)
                line[2] = line[2].replace("-", " -")
                line = " ".join(line)

                nline = line.split()
                kx = nline[3]
                ky = nline[4]
                kz = nline[5]
                kpoints.append(kx + " " + ky + " " + kz)
            elif line.find("energy") >= 0:
                nline = line.split()
                energies.append(nline[4])
            elif line.find("ion") >= 0:
                continue
            elif line.find("tot") >= 0:
                nline = line.split()
                tot.append(nline[10])
            else:
                continue

    datas = []
    for k in kpoints:
        for b in range(1, numband+1):
            datas.append(str(k) + " " + str(b))

    # reconstruct "tot" list to 4-pair list (density, Sx, Sy, Sz).
    tot = [tot[i:i+4] for i in range(0, len(tot), 4)]

    fdatas = []
    for (i, j, k) in zip(datas, energies, tot):
        strtot = list(map(str, k))
        strtot = " ".join(strtot)
        s = str(i) + " " + str(j) + " " + strtot
        fdatas.append(s)

    # write fdatas to outFile
    outfile = args.outFile
    with open(outfile, mode='w', encoding='utf-8') as f:
        for line in fdatas:
            f.write(line + "\n")


def scriptBandsplot(args):

    with open(args.file, mode='r', encoding='utf-8') as f:
        '''process data from args.file to dictionary type data
        data = {
        band_num1: [[kpoint1, energy1, Sx, Sy, Sz], [kpoint2, energy2, Sx, Sy, Sz], ...],
        band_num2: ...
        '''
        kpoints = []
        data = {}
        for line in f:
            parts = line.split()
            band_num = int(parts[3])
            kpoint = float(parts[0])    # kx only
            energy = float(parts[4])
            sx = float(parts[6])
            sy = float(parts[7])
            sz = float(parts[8])

            k_e_s = [kpoint, energy, sx, sy, sz]
            kpoints.append(kpoint)

            if band_num in data:
                data[band_num].append(k_e_s)
            else:
                data[band_num] = [k_e_s]

    # clear k-point duplicates
    kpoints_unique = []
    kpoints = list(map(str, kpoints))
    for k in kpoints:
        if k not in kpoints_unique:
            kpoints_unique.append(k)
    kpoints = list(map(float, kpoints_unique))

    # get band number list
    band_list = sorted(data.keys())
    # get energy per bands
    energies = []
    '''
     band1               band2
    [[..., ..., ...], [..., ..., ...], ...]
    '''
    for i in band_list:
        ene = []
        for x in data[i]:
            ene.append(x[1])
        energies.append(ene)

    # get spin components
    spin = []
    colors = []
    if args.spin is not 0:
        if args.spin == 1:
            s_index = 2
        elif args.spin == 2:
            s_index = 3
        else:
            s_index = 4
    else:
        s_index = False

    if args.band:
        plotspin = args.band
    elif args.mask:
        plotspin = [b for b in band_list if b not in args.mask]
    else:
        plotspin = band_list

    for i in band_list:
        sp = []
        color_ = []
        for a in data[i]:
            if s_index is not False and i in plotspin:
                # translate from magnetization to spin direction
                s = a[s_index] * (-1)
                if s >= 0:
                    color_.append('green')
                else:
                    color_.append('magenta')
            else:
                s = 0
            sp.append(math.fabs(s * args.markersize))
            #sp.append(math.fabs(s))
        spin.append(sp)
        colors.append(color_)


    plt.figure(1)
    plt.clf()
    plt.rcParams['font.family'] = 'sans-serif'

    plt.hlines(0, xmin=-0.5, xmax=0.5, linestyle=':', linewidth=0.5)
    plt.vlines(0, ymin=-2, ymax=2, linestyle='-', linewidth=0.3)

    # plot band-dispersion
    for i in band_list:
        # set Fermi energy as zero.
        energy_list = [x - args.fermi for x in energies[i - 1]]
        plt.plot(kpoints, energy_list, linewidth=0.8, color="black", linestyle='-')

    # plot spin-polarization
    for i in band_list:
        energy_list = [x - args.fermi for x in energies[i - 1]]
        plt.scatter(kpoints, energy_list, s=spin[i - 1],
                    linewidths=0.9, edgecolors=colors[i - 1], facecolors='None')

    #plt.xlabel('$k_x$', fontsize=15)
    plt.xticks(np.arange(-1.0, 1.0, 0.5))
    plt.yticks(np.arange(-2.0, 2.0, 0.5))
    plt.tick_params(direction='in')
    plt.ylim(args.elimit)
    plt.xlim([min(kpoints), max(kpoints)])
    plt.show()

if __name__ == "__main__":
    import argparse

    description = ("spinplot.py: a python3 script to display bandstructure "
                   "and spin-texture from VASP's PROCAR file"
                   "This script can handle only non-collinear calc data.")
    # A top-level parser
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='sub-command')

    ########## filter ##########
    phelp = '''
            extract and write necessary data from "inFile" to "outFile".
            outFile data form is 
            "kx ky kz bandNumber energy density(?) Sx Sy Sz".
            '''
    parserFilter = subparsers.add_parser('filter', help=phelp)

    phelp = 'Input filename. In most cases, it is "PROCAR".'
    parserFilter.add_argument('inFile', help=phelp)

    phelp = "Output filename."
    parserFilter.add_argument('outFile', help=phelp)

    VerbFilter = parserFilter.add_mutually_exclusive_group()
    VerbFilter.add_argument('-v', '--verbose', action='store_true')
    VerbFilter.add_argument('-q', '--quiet', action='store_true')

    parserFilter.set_defaults(func=scriptFilter)

    ########## bandsplot ##########
    phelp = '''Bandstructure and spin-texture plot. you should indicate 
               input file from filter sub-command.
            '''
    parserBandsplot = subparsers.add_parser('bandsplot', help=phelp)

    phelp = "Input file getting filter sub-command. "
    parserBandsplot.add_argument('file', help=phelp)


    VerbBandsplot = parserBandsplot.add_mutually_exclusive_group()
    VerbBandsplot.add_argument('-v', '--verbose', action='store_true')
    VerbBandsplot.add_argument('-q', '--quiet', action='store_true')

    selectBandsplot = parserBandsplot.add_mutually_exclusive_group()
    phelp = "select bands what you want spin-texture. " \
            "if you want spin-texture of bandNumber 121 and 122, you should " \
            "`--band 121 122`. Default: all band selected"
    selectBandsplot.add_argument('-b', '--band', type=int, nargs='+',
                                 help=phelp)

    phelp = "select bands what you don't want spin-texture. " \
            "if you don't want spin-texture of bandNumber 110 and 111, " \
            "you should `--mask 110 111`. Default: all band not selected"
    selectBandsplot.add_argument('-m', '--mask', type=int, nargs='+',
                                 help=phelp)


    phelp = "Set the Fermi energy (or any reference energy) as zero energy." \
            "To get it you should `grep E-fermi` the self-consistent OUTCAR."
    parserBandsplot.add_argument('-f', '--fermi', type=float, help=phelp)

    phelp = "Min/Max energy to be ploted. To plot [-1,1] centered in E_F:" \
            "`--elimit -1 1` or `-e -1 1`"
    parserBandsplot.add_argument('-e', '--elimit', type=float, nargs=2, help=phelp)

    phelp = "Spin component to be used: nonspin=0, sx=1, sy=2, sz=3." \
            " Default: s=0"
    parserBandsplot.add_argument('-s', '--spin', type=int, choices=[0, 1, 2, 3],
                                 default=0, help=phelp)

    phelp = "Spin marker(circle) size. you should do try and error... " \
            "Default: 250"
    parserBandsplot.add_argument('-ms', '--markersize', type=float,
                                 default=250, help=phelp)

    parserBandsplot.set_defaults(func=scriptBandsplot)

    args = parser.parse_args()
    args.func(args)
