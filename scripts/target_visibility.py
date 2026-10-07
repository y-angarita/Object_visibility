#!/usr/bin/env python3

import argparse
from pathlib import Path

from visibility.calculator import calculate_visibility, plot_visibility


def parse_args():
    parser = argparse.ArgumentParser(description="Calculate astronomical target visibility.")

    parser.add_argument("--observatory", default="OPD")
    parser.add_argument("--lat", type=float, default=-22.534444)
    parser.add_argument("--lon", type=float, default=-45.582500)
    parser.add_argument("--height", type=float, default=1864.0)
    parser.add_argument("--timezone", default="America/Sao_Paulo")
    parser.add_argument("--date", default="2026-11-15")
    parser.add_argument("--gal-lon", type=float, default=240.0)
    parser.add_argument("--gal-lat", type=float, default=-40.0)
    parser.add_argument("--altitude-limit", type=float, default=30.0)
    parser.add_argument("--output", default="object_visibility.png")
    parser.add_argument("--show", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    result = calculate_visibility(observatory_name=args.observatory,
    							  latitude=args.lat,
    							  longitude=args.lon,
    							  height_m=args.height,
    							  timezone_name=args.timezone,
    							  date_string=args.date,
    							  galactic_longitude=args.gal_lon,
    							  galactic_latitude=args.gal_lat,
    							  altitude_limit=args.altitude_limit,
    							  )

    for start, end in result["visibility_intervals"]:
        print(f"Visible: {start:.2f}–{end:.2f} hours relative to midnight")

    figure = plot_visibility(result)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=300, bbox_inches="tight")

    if args.show:
        import matplotlib.pyplot as plt
        plt.show()
    else:
        import matplotlib.pyplot as plt
        plt.close(figure)


if __name__ == "__main__":
    main()
