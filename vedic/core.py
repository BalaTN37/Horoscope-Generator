from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import math
import swisseph as swe
import os

ZODIAC_SIGNS = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]

PLANET_ORDER = [
    ('Sun', swe.SUN), ('Moon', swe.MOON), ('Mars', swe.MARS), ('Mercury', swe.MERCURY),
    ('Jupiter', swe.JUPITER), ('Venus', swe.VENUS), ('Saturn', swe.SATURN)
]

ABBR = {'Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me','Jupiter':'Ju','Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke'}

# Vimshottari dasha constants
NAK_LEN_DEG = 360.0 / 27.0  # 13°20'
VIM_MD_YEARS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17,
}
VIM_SEQUENCE = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
NAK_LORDS = [
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury', # Ashwini..Ashlesha (0..8)
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury', # Magha..Jyeshtha (9..17)
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'  # Mula..Revati (18..26)
]


def _julday(dt_utc: datetime) -> float:
    ut = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0 + dt_utc.microsecond/3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut)


def _ayanamsa_mode(name: str) -> int:
    n = (name or '').lower()
    if n in ('lahiri','kp','krishnamurti'):
        return swe.SIDM_LAHIRI
    # default to Lahiri
    return swe.SIDM_LAHIRI


def _house_system_code(name: str) -> bytes:
    n = (name or '').lower()
    if n in ('equal','e'):
        return b'E'
    if n in ('placidus','p'):
        return b'P'
    if n in ('koch','k'):
        return b'K'
    if n in ('porphyry','o'):
        return b'O'
    if n in ('regiomontanus','r'):
        return b'R'
    if n in ('campanus','c'):
        return b'C'
    if n in ('whole','w','whole_sign','whole-sign','whole sign'):
        # we will simulate whole sign houses separately using equal cusps
        return b'E'
    return b'E'


def _degnorm(d: float) -> float:
    return d % 360.0


def _sign_index(lon: float) -> int:
    return int(math.floor(_degnorm(lon) / 30.0))


def _deg_in_sign(lon: float) -> float:
    return _degnorm(lon) % 30.0


def _choose_iflag(ephe_dir: Optional[str]) -> int:
    """Choose Swiss Ephemeris flags based on availability of ephemeris files."""
    # Prefer SWIEPH if ephemeris files exist in ephe_dir; otherwise use MOSEPH
    if ephe_dir and os.path.isdir(ephe_dir):
        try:
            swe.set_ephe_path(ephe_dir)
            return swe.FLG_SIDEREAL | swe.FLG_SWIEPH
        except Exception:
            pass
    return swe.FLG_SIDEREAL | swe.FLG_MOSEPH


def compute_chart(birth_dt_local: datetime, lat: float, lon: float, tz_offset_hours: float, ayanamsa: str, house_system: str,
                  ephe_dir: Optional[str] = None, node_type: str = 'mean') -> Dict[str, Any]:
    # Convert local time by provided offset to UTC
    birth_dt_utc = birth_dt_local - timedelta(hours=tz_offset_hours)
    birth_dt_utc = birth_dt_utc.replace(tzinfo=timezone.utc)
    jd_ut = _julday(birth_dt_utc)

    # Configure Swiss Ephemeris for sidereal zodiac; choose SWIEPH if ephemeris files are present
    swe.set_sid_mode(_ayanamsa_mode(ayanamsa))
    iflag = _choose_iflag(ephe_dir)

    # Planets
    planets_sidereal: Dict[str, float] = {}
    for name, ipl in PLANET_ORDER:
        xx, ret = swe.calc_ut(jd_ut, ipl, iflag)
        lon = xx[0]
        planets_sidereal[name] = _degnorm(lon)
    # Nodes
    node_code = swe.MEAN_NODE if (node_type.lower() in ('mean','m')) else swe.TRUE_NODE
    xxn, ret = swe.calc_ut(jd_ut, node_code, iflag)
    node_lon = xxn[0]
    planets_sidereal['Rahu'] = _degnorm(node_lon)
    planets_sidereal['Ketu'] = _degnorm(node_lon + 180.0)

    # Houses and Ascendant
    hsys = _house_system_code(house_system)
    houses_res = swe.houses_ex(jd_ut, lat, lon, hsys, iflag)
    # houses_ex returns (cusps[0..11], ascmc[0..7]) as two tuples
    cusps, ascmc = houses_res
    asc_tropical = ascmc[0]  # ASC
    # asc returned is already aligned to current zodiac flags; ensure sidereal normalization
    asc_sid = _degnorm(asc_tropical)

    # If user asked for whole-sign, rebuild cusps from asc sidereal at 0 deg of asc sign
    if house_system.lower() in ('whole','w','whole-sign','wholesign','whole sign'):
        asc_sign_start = 30.0 * _sign_index(asc_sid)
        cusps_map = {i: _degnorm(asc_sign_start + (i-1)*30.0) for i in range(1,13)}
    else:
        # cusps tuple is 12 elements, index 0..11
        cusps_map = {i+1: _degnorm(cusps[i]) for i in range(12)}

    # Transit now (sidereal)
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    jd_now = _julday(now_utc)
    swe.set_sid_mode(_ayanamsa_mode(ayanamsa))
    trans_sid: Dict[str, float] = {}
    for name, ipl in PLANET_ORDER:
        xx_now, _ = swe.calc_ut(jd_now, ipl, iflag)
        lon = xx_now[0]
        trans_sid[name] = _degnorm(lon)
    xxn_now, _ = swe.calc_ut(jd_now, node_code, iflag)
    node_lon_now = xxn_now[0]
    trans_sid['Rahu'] = _degnorm(node_lon_now)
    trans_sid['Ketu'] = _degnorm(node_lon_now + 180.0)

    # Prepare outputs
    def sign_name(lon):
        return ZODIAC_SIGNS[_sign_index(lon)]

    planets_out = {}
    for name, lonv in planets_sidereal.items():
        planets_out[name] = {
            'longitude': round(lonv, 6),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        }

    trans_out = {}
    for name, lonv in trans_sid.items():
        trans_out[name] = {
            'longitude': round(lonv, 6),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        }

    # House assignment using cusp boundaries: a planet is in house i if it lies between cusp[i] and cusp[i+1] along zodiac
    cusp_list = [cusps_map[i] for i in range(1,13)]
    def in_arc(a, start, end):
        start = _degnorm(start); end = _degnorm(end); a = _degnorm(a)
        if start <= end:
            return start <= a < end
        else:
            return a >= start or a < end
    def house_index_for(lonv: float) -> int:
        for i in range(12):
            start = cusp_list[i]
            end = cusp_list[(i+1) % 12]
            if in_arc(lonv, start, end):
                return i+1
        return 12

    planets_by_house: Dict[str, List[Dict[str, Any]]] = {str(i): [] for i in range(1,13)}
    for name, lonv in planets_sidereal.items():
        hi = house_index_for(lonv)
        planets_by_house[str(((hi - 1) % 12) + 1)].append({
            'name': name,
            'abbr': ABBR.get(name, name[:2]),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        })

    # Vimshottari Mahadasha/Antardasha/Pratyantardasha based on birth Moon nakshatra
    def _vim_mds(birth_local: datetime, moon_lon_sidereal: float):
        # Determine nakshatra and its lord
        nak_index = int(math.floor(_degnorm(moon_lon_sidereal) / NAK_LEN_DEG))  # 0..26
        nak_offset_deg = _degnorm(moon_lon_sidereal) - nak_index * NAK_LEN_DEG
        lord = NAK_LORDS[nak_index]
        total_years = VIM_MD_YEARS[lord]
        # Remaining proportion in current nakshatra
        frac_remaining = 1.0 - (nak_offset_deg / NAK_LEN_DEG)
        remaining_years_current = total_years * frac_remaining

        # Compute the start of current MD by subtracting elapsed from birth
        elapsed_years_current = total_years - remaining_years_current

        def add_years_calendar(dt: datetime, years: int) -> datetime:
            try:
                return dt.replace(year=dt.year + years)
            except ValueError:
                # handle Feb 29 -> Feb 28 fallback
                return dt.replace(month=2, day=28, year=dt.year + years)

        def add_years_fractional(dt: datetime, years_fraction: float, sign: int = +1) -> datetime:
            days = years_fraction * 365.2425
            return dt + timedelta(days=sign * days)

        # Start of current MD
        start_current = birth_local
        # Subtract integer years then fractional portion to get the MD start
        int_elapsed = int(math.floor(elapsed_years_current))
        frac_elapsed = elapsed_years_current - int_elapsed
        if int_elapsed:
            start_current = add_years_calendar(start_current, -int_elapsed)
        if abs(frac_elapsed) > 1e-9:
            start_current = add_years_fractional(start_current, frac_elapsed, sign=-1)

        # Helper to rotate Vim sequence so it starts with a given lord
        def rotate_seq(start_lord: str) -> List[str]:
            idx = VIM_SEQUENCE.index(start_lord)
            return VIM_SEQUENCE[idx:] + VIM_SEQUENCE[:idx]

        # Build 9 Mahadashas from current lord following the sequence
        mds = []
        cur_md_start = start_current
        for md_lord in rotate_seq(lord):
            md_years = VIM_MD_YEARS[md_lord]
            md_end = add_years_calendar(cur_md_start, md_years)

            # Antardashas inside this Mahadasha
            ads = []
            cur_ad_start = cur_md_start
            # AD duration proportion within MD: MD_length * (AD_lord_years / 120)
            md_total_years = float(md_years)
            ad_seq = rotate_seq(md_lord)
            for i, ad_lord in enumerate(ad_seq):
                frac = VIM_MD_YEARS[ad_lord] / 120.0
                ad_years_equiv = md_total_years * frac
                # use fractional-year addition for sub-periods
                ad_end = add_years_fractional(cur_ad_start, ad_years_equiv, sign=+1)
                # Ensure last AD ends exactly at MD end to avoid drift
                if i == len(ad_seq) - 1:
                    ad_end = md_end

                # Pratyantardashas inside this Antardasha
                pds = []
                cur_pd_start = cur_ad_start
                ad_total_years = ad_years_equiv
                pd_seq = rotate_seq(ad_lord)
                for j, pd_lord in enumerate(pd_seq):
                    pd_frac = VIM_MD_YEARS[pd_lord] / 120.0
                    pd_years_equiv = ad_total_years * pd_frac
                    pd_end = add_years_fractional(cur_pd_start, pd_years_equiv, sign=+1)
                    if j == len(pd_seq) - 1:
                        pd_end = ad_end
                    pds.append({
                        'lord': pd_lord,
                        'start': cur_pd_start.isoformat(),
                        'end': pd_end.isoformat(),
                    })
                    cur_pd_start = pd_end

                ads.append({
                    'lord': ad_lord,
                    'start': cur_ad_start.isoformat(),
                    'end': ad_end.isoformat(),
                    'pratyantardashas': pds,
                })
                cur_ad_start = ad_end

            mds.append({
                'lord': md_lord,
                'start': cur_md_start.isoformat(),
                'end': md_end.isoformat(),  # end is exclusive; display may show previous day
                'years': md_years,
                'antardashas': ads,
            })
            cur_md_start = md_end

        return {
            'nakshatraIndex': nak_index,
            'nakshatraLord': lord,
            'balanceAtBirthYears': remaining_years_current,
            'mahadashas': mds,
        }

    vim = _vim_mds(birth_dt_local, planets_sidereal['Moon'])

    return {
        'meta': {
            'jd_ut': jd_ut,
            'ayanamsa': ayanamsa,
            'house_system': house_system,
        },
        'ascendant': round(asc_sid, 6),
        'houses': {str(k): round(v, 6) for k, v in cusps_map.items()},
        'planets': planets_out,
        'planetsByHouse': planets_by_house,
        'transits': trans_out,
        'vimshottari': vim,
    }
