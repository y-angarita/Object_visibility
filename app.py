from datetime import date

import matplotlib.pyplot as plt
import streamlit as st

from visibility.calculator import calculate_visibility, plot_visibility


st.set_page_config(page_title="Object Visibility",
				   page_icon="🌌", layout="wide")

st.title("Astronomical Object Visibility")
st.caption("Visibility of a Galactic-coordinate target from a selected observatory.")

with st.sidebar:
    st.header("Observatory")

    observatory_name = st.text_input("Name", value="OPD")

    latitude = st.number_input("Latitude [deg]",
    						   value=-22.534444,
    						   min_value=-90.0,
    						   max_value=90.0,
    						   format="%.6f",
    						   )

    longitude = st.number_input("Longitude [deg]",
    							value=-45.582500,
    							min_value=-180.0,
    							max_value=180.0,
    							format="%.6f",
    							)

    height_m = st.number_input("Height [m]",
    						   value=1864.0,
    						   min_value=0.0,
    						   format="%.1f",
    						   )

    timezone_name = st.text_input("IANA timezone", value="America/Sao_Paulo")

    st.header("Target and observing date")

    observing_date = st.date_input("Local calendar date", value=date(2026, 11, 15))

    galactic_longitude = st.number_input("Galactic longitude l [deg]",
    									 value=240.0,
    									 min_value=0.0,
    									 max_value=360.0,
    									 format="%.3f",
    									 )

    galactic_latitude = st.number_input("Galactic latitude b [deg]",
    									value=-40.0,
    									min_value=-90.0,
    									max_value=90.0,
    									format="%.3f",
    									)

    altitude_limit = st.slider("Minimum target altitude [deg]",
    						   min_value=0.0,
    						   max_value=90.0,
    						   value=30.0,
    						   step=1.0,
    						   )

    calculate = st.button("Calculate visibility", type="primary", 
    					  use_container_width=True)

if calculate:
    try:
        with st.spinner("Calculating astronomical visibility..."):
            result = calculate_visibility(observatory_name=observatory_name,
            							  latitude=latitude,
            							  longitude=longitude,
            							  height_m=height_m,
            							  timezone_name=timezone_name,
            							  date_string=observing_date.isoformat(),
            							  galactic_longitude=galactic_longitude,
            							  galactic_latitude=galactic_latitude,
            							  altitude_limit=altitude_limit,
            							  )

            figure = plot_visibility(result)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Moon phase", result["phase_text"])

        with col2:
            illumination = result["mean_night_illumination"]
            if illumination == illumination:
                st.metric("Mean night illumination", f"{illumination * 100:.1f}%")
            else:
                st.metric("Mean night illumination", "Unavailable")

        with col3:
            st.metric("Visible intervals", len(result["visibility_intervals"]))

        st.pyplot(figure, clear_figure=True)

        st.subheader("Visibility intervals")

        if result["visibility_intervals"]:
            for start, end in result["visibility_intervals"]:
                start_clock = start % 24
                end_clock = end % 24

                st.write(f"{start_clock:05.2f}–{end_clock:05.2f} "
                		 "relative to local midnight")
        else:
            st.info("The target is not visible under the selected constraints.")

        plt.close(figure)

    except Exception as error:
        st.error(f"Calculation failed: {error}")
