from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body, get_sun

from astropy.time import Time
from astroplan import Observer, moon_illumination, moon_phase_angle


def phase_label(illumination: float, signed_elongation: float) -> str:
    """
    Return a descriptive lunar phase label.

    Parameters
    ----------
    illumination : float
        Illuminated fraction, approximately from 0 to 1.

    signed_elongation : float
        Signed Sun–Moon ecliptic longitude separation in degrees.
    """
    if illumination < 0.01:
        return "New Moon"

    if illumination > 0.99:
        return "Full Moon"

    if 0.45 <= illumination <= 0.55:
        return "First quarter" if signed_elongation > 0 else "Third quarter"

    if signed_elongation > 0:
        return "Waxing crescent" if illumination < 0.5 else "Waxing gibbous"

    return "Waning crescent" if illumination < 0.5 else "Waning gibbous"


def contiguous_intervals(x: np.ndarray, mask: np.ndarray) -> list[tuple[float, float]]:
    """
    Return contiguous intervals in x where mask is True.

    Parameters
    ----------
    x : array-like
        Coordinates corresponding to the Boolean mask.

    mask : array-like of bool
        Boolean condition.

    Returns
    -------
    intervals : list of tuple
        List of (start, end) intervals.
    """
    mask = np.asarray(mask, dtype=bool)
    x = np.asarray(x)

    if not np.any(mask):
        return []

    starts = np.flatnonzero(mask & ~np.r_[False, mask[:-1]])
    ends = np.flatnonzero(mask & ~np.r_[mask[1:], False])

    return [(float(x[start]), float(x[end])) for start, end in zip(starts, ends)]


def make_observer(observatory_name: str,
				  latitude: float,
				  longitude: float,
				  height_m: float,
				  timezone_name: str,
				  ) -> Observer:
				   
				  
    location = EarthLocation(lat=latitude * u.deg,
				  			 lon=longitude * u.deg,
				  			 height=height_m * u.m)

    return Observer(location=location, name=observatory_name, timezone=timezone_name)


def local_midnight(date_string: str, timezone_name: str) -> datetime:
    tz = ZoneInfo(timezone_name)
    return datetime.fromisoformat(f"{date_string} 00:00:00").replace(tzinfo=tz)


def find_twilight_times(observer: Observer,
						date_string: str,
						timezone_name: str) -> tuple[Time, Time]:
						
    midnight_local = local_midnight(date_string, timezone_name)
    midnight_utc = Time(midnight_local.astimezone(timezone.utc), scale="utc")

    evening = observer.twilight_evening_astronomical(midnight_utc,
    												 which="nearest",
    												 n_grid_points=300)

    morning = observer.twilight_morning_astronomical(midnight_utc,
    												 which="next",
    												 n_grid_points=300)
    												 
    return evening, morning


def time_to_plot_hour(astropy_time: Time,
					  local_midnight_datetime: datetime,
					  timezone_name: str,
					  ) -> float:
					  
    tz = ZoneInfo(timezone_name)

    local_datetime = astropy_time.to_datetime(timezone=tz)

    return (local_datetime - local_midnight_datetime).total_seconds() / 3600.0


def calculate_visibility(observatory_name: str = "OPD",
						 latitude: float = -22.534444,
						 longitude: float = -45.582500,
						 height_m: float = 1864.0,
						 timezone_name: str = "America/Sao_Paulo",
						 date_string: str = "2026-11-15",
						 galactic_longitude: float = 240.0,
						 galactic_latitude: float = -40.0,
						 altitude_limit: float = 30.0,
						 time_step_minutes: int = 5,
						 ) -> dict:
						 
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90 degrees.")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    if altitude_limit < 0 or altitude_limit > 90:
        raise ValueError("Altitude limit must be between 0 and 90 degrees.")

    observer = make_observer(observatory_name=observatory_name,
    						 latitude=latitude,
    						 longitude=longitude,
    						 height_m=height_m,
    						 timezone_name=timezone_name)

    location = observer.location
    midnight_local = local_midnight(date_string, timezone_name)

    local_start = midnight_local - timedelta(hours=12)
    local_end = midnight_local + timedelta(hours=12)

    utc_start = local_start.astimezone(timezone.utc)
    utc_end = local_end.astimezone(timezone.utc)

    duration_seconds = (utc_end - utc_start).total_seconds()
    n_times = int(duration_seconds / (time_step_minutes * 60)) + 1

    utc_datetimes = [utc_start + timedelta(minutes=time_step_minutes * i)
    				 for i in range(n_times)]

    times = Time(utc_datetimes, scale="utc")

    tz = ZoneInfo(timezone_name)
    local_datetimes = [dt.astimezone(tz) for dt in utc_datetimes]

    plot_hours = np.array([(dt - midnight_local).total_seconds() / 3600.0
						   for dt in local_datetimes])

    evening_twilight, morning_twilight = find_twilight_times(observer,
    														 date_string,
    														 timezone_name)

    evening_plot_hour = time_to_plot_hour(evening_twilight,
    									  midnight_local,
    									  timezone_name)

    morning_plot_hour = time_to_plot_hour(morning_twilight, 
    									  midnight_local,
    									  timezone_name)

    target = SkyCoord(l=galactic_longitude * u.deg, b=galactic_latitude * u.deg,
    				  frame="galactic")

    altaz_frame = AltAz(obstime=times, 
    					location=location,
    					pressure=0 * u.hPa,
    					temperature=10 * u.deg_C,
    					relative_humidity=0,
    					obswl=550 * u.nm,
    					)

    target_altaz = target.transform_to(altaz_frame)
    sun_altaz = get_sun(times).transform_to(altaz_frame)
    moon_altaz = get_body("moon", times, location=location).transform_to(altaz_frame)

    target_altitude = target_altaz.alt.to_value(u.deg)
    sun_altitude = sun_altaz.alt.to_value(u.deg)
    moon_altitude = moon_altaz.alt.to_value(u.deg)

    target_airmass = np.asarray(target_altaz.secz.value, dtype=float)

    target_airmass[target_altitude <= 0] = np.nan
    target_airmass[target_airmass > 10] = np.nan

    illumination = np.asarray(moon_illumination(times), dtype=float)

    phase_angle = np.asarray(moon_phase_angle(times), dtype=float)

    sun_coordinates = get_sun(times)
    moon_coordinates = get_body("moon", times, location=location)

    elongation_signed = (moon_coordinates.geocentrictrueecliptic.lon.wrap_at(180 * u.deg)
    					- sun_coordinates.geocentrictrueecliptic.lon.wrap_at(180 * u.deg)
    					).wrap_at(180 * u.deg).to_value(u.deg)

    astronomical_night = ((plot_hours >= evening_plot_hour)
    					  & (plot_hours <= morning_plot_hour))

    target_visible = (astronomical_night & (target_altitude >= altitude_limit))

    if np.any(astronomical_night):
        mean_night_illumination = float(np.nanmean(illumination[astronomical_night]))
    else:
        mean_night_illumination = np.nan

    phase_text = phase_label(float(np.nanmean(illumination)),
    						 float(np.nanmean(elongation_signed)))

    visibility_intervals = contiguous_intervals(plot_hours, target_visible)

    return {"observatory_name": observatory_name,
    		"date_string": date_string,
    		"timezone_name": timezone_name,
    		"target": target,
    		"times": times,
    		"utc_datetimes": utc_datetimes,
    		"plot_hours": plot_hours,
    		"target_altitude": target_altitude,
    		"sun_altitude": sun_altitude,
    		"moon_altitude": moon_altitude,
    		"target_airmass": target_airmass,
    		"illumination": illumination,
    		"phase_angle": phase_angle,
    		"astronomical_night": astronomical_night,
    		"target_visible": target_visible,
    		"altitude_limit": altitude_limit,
    		"evening_twilight": evening_twilight,
    		"morning_twilight": morning_twilight,
    		"evening_plot_hour": evening_plot_hour,
    		"morning_plot_hour": morning_plot_hour,
    		"mean_night_illumination": mean_night_illumination,
    		"phase_text": phase_text,
    		"visibility_intervals": visibility_intervals,
    		}


def plot_visibility(result: dict):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    plot_hours = result["plot_hours"]

    ax1.plot(plot_hours, result["target_altitude"], color="tab:blue", 
    		 linewidth=2, label="Target")

    ax1.plot(plot_hours, result["moon_altitude"], color="0.35", linewidth=1.2,
    		 linestyle=":", label="Moon")

    ax1.plot(plot_hours, result["sun_altitude"], color="goldenrod", linewidth=1.2, 
    		 linestyle="-.", label="Sun")

    ax1.fill_between(plot_hours, 0, 90, where=result["astronomical_night"], color="navy", 
    				 alpha=0.08, label="Astronomical night")

    ax1.axhline(result["altitude_limit"], color="tab:blue", linestyle="--", linewidth=1, 
    			label=f'Altitude limit: {result["altitude_limit"]:.1f}°')

    ax1.axvline(result["evening_plot_hour"], color="purple", linestyle="--", 
    			linewidth=1.2)

    ax1.axvline(result["morning_plot_hour"], color="purple", linestyle="--", 
    			linewidth=1.2)

    ax1.axvline(0, color="0.5", linestyle="--", linewidth=1)
    ax1.axvline(12, color="0.5", linestyle=":", linewidth=1)

    x_ticks = np.arange(-12, 13, 2)
    local_labels = [f"{int(x % 24):02d}:00" for x in x_ticks]

    utc_labels = []
    for x in x_ticks:
        index = np.argmin(np.abs(plot_hours - x))
        utc_labels.append(result["utc_datetimes"][index].strftime("%H:%M"))

    ax1.set_xlim(-12, 12)
    ax1.set_ylim(0, 90)
    ax1.set_xticks(x_ticks)
    ax1.set_xticklabels(local_labels)
    ax1.set_xlabel("Local civil time")
    ax1.set_ylabel("Elevation (degrees)")
    ax1.set_yticks(np.arange(0, 91, 10))
    ax1.grid(alpha=0.3)

    ax_airmass = ax1.twinx()

    airmass_ticks = np.array([1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0, 5.0])

    airmass_altitudes = np.degrees(np.arcsin(1.0 / airmass_ticks))

    ax_airmass.set_ylim(ax1.get_ylim())
    ax_airmass.set_yticks(airmass_altitudes)
    ax_airmass.set_yticklabels([f"{value:g}" for value in airmass_ticks])
    ax_airmass.set_ylabel("Airmass", color="tab:green")
    ax_airmass.tick_params(axis="y", colors="tab:green")

    ax_utc = ax1.twiny()
    ax_utc.set_xlim(-12, 12)
    ax_utc.set_xticks(x_ticks)
    ax_utc.set_xticklabels(utc_labels)
    ax_utc.set_xlabel("UTC")

    mean_illumination = result["mean_night_illumination"]

    if np.isfinite(mean_illumination):
        illumination_text = (f"Mean astronomical-night Moon illumination: {mean_illumination * 100:.1f}%")
    else:
        illumination_text = ("Mean astronomical-night Moon illumination: unavailable")

    title = (f"{result["observatory_name"]} — {result["date_string"]}\n{illumination_text} ({result['phase_text']})")

    ax1.set_title(title)
    ax1.legend(loc="upper right", fontsize=9)
    fig.tight_layout()

    return fig
