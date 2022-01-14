"""
Plot 3D or contour plot with 2 variables.
The format of source data is csv.
"""
import numpy as np
import pandas as pd


class CommonParams:
    def __init__(self,
                 input_file: str,
                 xlim: list,
                 ylim: list,
                 zlim: list,
                 skiprows=0):
        data = pd.read_csv(input_file, skiprows=1, header=0, index_col=0)
        Xgrid = data.columns.values.astype(np.float32)
        Ygrid = data.index.values.astype(np.float32)
        X, Y = np.meshgrid(Xgrid, Ygrid)
        Z = data.values


if __name__ == "__main__":
    import argparse

    description = "Plot 3D or contour plot with 2 variables." \
                  "The format of source data is csv."
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='sub-command')

    help = "input csv file name"
    parser.add_argument('input', help=help)

    # contour #
    help = "contour plot"
    parserContour = subparsers.add_parser('contour', help=help)

