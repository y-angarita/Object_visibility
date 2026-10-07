# Object Visibility

Calculate and visualize the visibility of an astronomical target (in Galactic coordinates) from a given observatory, including Sun/Moon altitude, astronomical night, and target airmass.

This package provides:

- A reusable Python module for visibility calculations.
- A command-line script to generate plots and summaries.
- A Streamlit web application for interactive use.

## Features

- Compute target, Sun, and Moon altitude over a 24-hour interval centered on a local date.
- Determine astronomical night using evening/morning astronomical twilight.
- Apply a minimum target altitude constraint.
- Estimate target airmass and mean Moon illumination during astronomical night.
- Produce a publication-quality plot with:
  - Local civil time and UTC axes.
  - Target, Sun, and Moon elevation.
  - Astronomical night shading.
  - Airmass scale on a secondary y-axis.
- Interactive Streamlit app for quick what-if studies of observatory, date, and target coordinates.

## Installation

Clone the repository:

```bash
git clone [https://github.com/y-angarita/Object_visibility.git](https://github.com/y-angarita/Object_visibility.git)
cd Object_visibility
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

### Command-line script

Generate a visibility plot and summary for a specific date and target:

```bash
python scripts/target_visibility.py \
  --observatory OPD \
  --lat -22.534444 \
  --lon -45.582500 \
  --height 1864 \
  --timezone America/Sao_Paulo \
  --date 2026-11-15 \
  --gal-lon 240 \
  --gal-lat -40 \
  --altitude-limit 30 \
  --output plots/object_visibility_OPD_2026-11-15.png
```

Key arguments:

- `--observatory`: Name of the observatory (for labels).
- `--lat`, `--lon`, `--height`: Observatory geodetic coordinates (degrees, metres).
- `--timezone`: IANA timezone name (e.g. `America/Sao_Paulo`).
- `--date`: Local calendar date (`YYYY-MM-DD`).
- `--gal-lon`, `--gal-lat`: Target Galactic longitude and latitude (degrees).
- `--altitude-limit`: Minimum target altitude in degrees.
- `--output`: Path to the output PNG file.
- `--show`: Open the plot window after saving (optional).

The script prints:

- Evening and morning astronomical twilight times (local time).
- Moon phase description and mean night illumination.
- Time intervals (in local time) when the target is above the altitude limit during astronomical night.

### Python API

Use the calculation module directly in your own scripts or notebooks:

```python
from visibility.calculator import calculate_visibility, plot_visibility

result = calculate_visibility(
    observatory_name="OPD",
    latitude=-22.534444,
    longitude=-45.582500,
    height_m=1864.0,
    timezone_name="America/Sao_Paulo",
    date_string="2026-11-15",
    galactic_longitude=240.0,
    galactic_latitude=-40.0,
    altitude_limit=30.0,
)

# Access arrays and metadata
plot_hours = result["plot_hours"]
target_altitude = result["target_altitude"]
visibility_intervals = result["visibility_intervals"]

# Generate and save a plot
fig = plot_visibility(result)
fig.savefig("object_visibility.png", dpi=300, bbox_inches="tight")
```

Key fields in `result`:

- `plot_hours`: Hours relative to local midnight (−12 to +12).
- `target_altitude`, `sun_altitude`, `moon_altitude`: Altitudes in degrees.
- `target_airmass`: Approximate airmass (sec z), NaN where not useful.
- `astronomical_night`: Boolean mask for astronomical night.
- `target_visible`: Boolean mask for “observable” intervals.
- `visibility_intervals`: List of (start, end) intervals in `plot_hours`.
- `phase_text`, `mean_night_illumination`: Moon phase description and illumination fraction.

### Streamlit application

Run the interactive web app locally:

```bash
streamlit run app.py
```

In the sidebar, set:

- Observatory name and coordinates.
- Timezone.
- Observing date.
- Target Galactic coordinates.
- Minimum target altitude.

Click **Calculate visibility** to:

- See the elevation plot with local time and UTC axes.
- Inspect Moon phase and mean night illumination.
- View the number and approximate times of visible intervals.

## Deployment on Streamlit Community Cloud

1. Push this repository to GitHub (e.g. `https://github.com/y-angarita/Object_visibility`).
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Create a new app:
   - Repository: `y-angarita/Object_visibility`
   - Branch: `main`
   - Main file path: `app.py`
4. Deploy.

Streamlit will install the packages from `requirements.txt` and serve the app.

## Project structure

```text
.
├── app.py
├── visibility/
│   ├── __init__.py
│   └── calculator.py
├── scripts/
│   └── target_visibility.py
├── tests/
│   └── test_calculator.py
├── requirements.txt
├── README.md
└── .gitignore
```

- `visibility/calculator.py`: Core calculations and plotting.
- `scripts/target_visibility.py`: Command-line interface.
- `app.py`: Streamlit application.
- `tests/`: Basic tests (extend as needed).

## Requirements

Main dependencies (see `requirements.txt`):

- `numpy`
- `matplotlib`
- `astropy`
- `astroplan`
- `streamlit`
- `healpy` (optional, currently not used in the core calculation)

Python 3.9+ is recommended (for `zoneinfo`).

## Copyright

© 2026 Yenifer Angarita Arenas. All rights reserved.

This software is provided for research and educational use. Redistribution, modification, or commercial use requires explicit permission from the copyright holder.

## Acknowledgements

- Astropy and Astroplan communities for time, coordinate, and twilight tools.
- OPD (Observatório do Pico dos Dias) and other observatories for motivating this tool.
