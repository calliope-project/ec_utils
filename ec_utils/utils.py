"""Utility functions."""

import logging
from typing import Literal, Optional

import pandas as pd
import pycountry
import xarray as xr

LOGGER = logging.getLogger(__name__)


def eu_country_code_to_iso3(eu_country_code):
    """Converts EU country code to ISO 3166 alpha 3.

    The European Union uses its own country codes, which do not always match ISO 3166.
    """
    assert (
        len(eu_country_code) == 2
    ), f"EU country codes are of length 2, yours is '{eu_country_code}'."

    return convert_country_code(eu_country_code, output="alpha3")


def convert_country_code(
    input_country: str,
    output: Literal["alpha2", "alpha2_eu", "alpha3", "name"] = "alpha3",
) -> str:
    """Converts input country code into pycountry names or alpha codes.

    Args:
        input_country (str): Country code/name to convert. Can accept EU country codes.
        output (Literal[alpha2, alpha2_eu, alpha3, name], optional):
            Output format. Defaults to "alpha3". Options:

            - ISO alpha2: alpha2
            - ISO alpha2 with EU codes: alpha2_eu
            - ISO alpha3: alpha3
            - country name: name

    Returns:
        str: Input country converted to output format.
    """
    if input_country.lower() == "el":
        input_country = "gr"
    elif input_country.lower() == "uk":
        input_country = "gb"
    elif (
        input_country.lower() == "bh"
    ):  # this is a weird country code used in the biofuels dataset
        input_country = "ba"

    lookup = pycountry.countries.lookup(input_country)
    if output == "alpha2":
        converted = lookup.alpha_2

    if output == "alpha2_eu":
        alpha2 = lookup.alpha_2
        if alpha2 == "GB":
            converted = "UK"
        elif alpha2 == "GR":
            converted = "EL"
        else:
            converted = alpha2

    if output == "alpha3":
        converted = lookup.alpha_3

    if output == "name":
        converted = lookup.name

    return converted


def convert_valid_countries(
    country_codes: list,
    output: str = "alpha3",
    errors: Literal["raise", "ignore"] = "raise",
) -> dict:
    """Map country codes / names to uniform ISO country codes / pycountry names.

    Args:
        country_codes (list):
            Strings defining country codes / names.
            E.g., ["France", "FRA", "FR"] will all be treated the same.
        output (str, optional):
            pycountry output type, e.g. `alpha3` for 3-letter ISO standard.
            Defaults to "alpha3".
        errors (Literal["raise", "ignore"], optional):
            `raise` or `ignore` invalid country codes. Defaults to "raise".

    Raises:
        err: invalid country code detected, and `errors == 'raise'`.

    Returns:
        dict: Mapping from input countries to output countries for all valid cases.
    """
    mapped_codes = {}
    for country_code in country_codes:
        try:
            mapped_codes[country_code] = convert_country_code(
                country_code, output=output
            )
        except LookupError as err:
            if errors == "raise":
                raise err
            elif errors == "ignore":
                LOGGER.info(f"Skipping country/region {country_code}")
                continue
    return mapped_codes


def rename_and_groupby(
    da: xr.DataArray,
    rename_dict: dict,
    dim_name: str,
    new_dim_name: Optional[str] = None,
    dropna: bool = False,
    drop_other_dim_items: bool = True,
) -> xr.DataArray:
    """Rename DataArray contents of a given dimension.

    Optionally, rename that dimension.

    If renaming the contents has some overlap (e.g. {'FRA': 'DEU', 'CHE': 'DEU'}),
    then the returned dataarray will be grouped over the new dimension items and summed.

    Args:
        da (xr.DataArray):
            Input dataarray with the dimension `dim_name`.
        rename_dict (dict):
            remap items in `dim_name` to new names ({"old": "new"}).
        dim_name (str):
            Dimension on which to rename items.
        new_dim_name (Optional[str], optional): Defaults to None.
            If not None, rename the dimension "dim_name" to the given string.
        dropna (bool, optional): Defaults to False.
            If True, drop items in "dim_name" with all NaN values in other dimensions.
        drop_other_dim_items (bool, optional): Defaults to True.
            If True, dimension items not referenced in `rename_dict` keys will be
            removed from that dimension in the returned array.

    Returns:
        (xr.DataArray): modified DataArray.
    """
    rename_series = pd.Series(rename_dict).rename_axis(index=dim_name)
    if drop_other_dim_items is False:
        existing_dim_items = da[dim_name].to_series()
        rename_series = rename_series.reindex(existing_dim_items).fillna(
            existing_dim_items
        )

    if new_dim_name is None:
        new_dim_name = f"_{dim_name}"  # placeholder that we'll revert
        revert_dim_name = True
    else:
        revert_dim_name = False

    rename_da = xr.DataArray(rename_series.rename(new_dim_name))
    da = (
        da.reindex({dim_name: rename_da[dim_name]})
        .groupby(rename_da)
        .sum(dim_name, skipna=True, min_count=1, keep_attrs=True)
    )
    if revert_dim_name:
        da = da.rename({new_dim_name: dim_name})
        new_dim_name = dim_name
    if dropna:
        da = da.dropna(new_dim_name, how="all")
    return da


def ktoe_to_twh(array):
    """Convert KTOE to TWH."""
    return array * 1.163e-2


def gwh_to_tj(array):
    """Convert GWh to TJ."""
    return array * 3.6


def pj_to_twh(array):
    """Convert PJ to TWh."""
    return array / 3.6


def tj_to_twh(array):
    """Convert TJ to TWh."""
    return pj_to_twh(array) / 1000


def tj_to_ktoe(array):
    """Convert TJ to Ktoe."""
    return array * 23.88e-3
