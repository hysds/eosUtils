########################################################################
#
# TITLE:
#	time.py
#
# AUTHOR:
#	Kevin J Miller
#
#	Copyright (C) 2003, California Institute of Technology.
#	U. S. Government Sponsorship acknowledged.
#
########################################################################

"""Standard GPS time functions."""

__version__ = '$Revision: 1.2 $'[11:-2]

import types

#
# exported constants
#
OneSecond = 1
OneMinute = OneSecond * 60
OneHour = OneMinute * 60
OneDay = OneHour * 24
OneWeek = OneDay * 7
MonthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December']
DayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
    'Saturday', 'Sunday']

def adoytoaymd(year, doy, hour=0, min=0, sec=0):
    """adoytoaymd(year, doy, hour, min, sec) -> (year, mon, day, hour, min, sec)

Convert an array time with a day-of-year to an array time with a month and day.
The hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    (mon, day) = _to_md[leap][doy]

    return (year, mon, day, hour, min, sec)

def adoytocdoy(year, doy, hour=0, min=0, sec=0):
    """adoytocdoy(year, doy, hour, min, sec) -> string

Convert an array time with a day-of-year to a standard CCSDS day-of-year time
string.  The hour, minute and second parameters are optional.  All input
parameters must be of type int."""

    #
    # validate input values
    #
    try:
	_val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return '%04d-%03dT%02d:%02d:%02d' % (year, doy, hour, min, sec)

def adoytocymd(year, doy, hour=0, min=0, sec=0):
    """adoytocymd(year, doy, hour, min, sec) -> string

Convert an array time with a day-of-year to a standard CCSDS year-month-day
time string.  The hour, minute and second parameters are optional.  All input
parameters must be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    (mon, day) = _to_md[leap][doy]

    return '%04d-%02d-%02dT%02d:%02d:%02d' % (year, mon, day, hour, min, sec)

def adoytodoy(year, doy, hour=0, min=0, sec=0):
    """adoytodoy(year, doy, hour, min, sec) -> string

Convert an array time with a day-of-year to a day-of-year time string.  The
hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	_val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return '%04d%03d%02d%02d%02d' % (year, doy, hour, min, sec)

def adoytomjd(year, doy, hour=0, min=0, sec=0):
    """adoytomjd(year, doy, hour, min, sec) -> mjd

Convert an array time with a day-of-year to the Modified Julian Day (i.e.,
fractional days since Midnight, Nov 17, 1858).  The hour, minute and second
parameters are optional.  All input parameters must be of type int."""

    #
    # validate input values
    #
    try:
	_val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    uet = _doy_to_uet(year, doy, hour, min, sec)

    return _uet_to_mjd(uet)

def adoytouet(year, doy, hour=0, min=0, sec=0):
    """adoytouet(year, doy, hour, min, sec) -> uet

Convert an array time with a day-of-year to the time in seconds since 1970
(UNIX epoch).  The hour, minute and second parameters are optional.  All
input parameters must be of type int.  This function returns a long int if
the result does not fit in an int."""

    #
    # validate input values
    #
    try:
	_val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return _doy_to_uet(year, doy, hour, min, sec)

def adoytoymd(year, doy, hour=0, min=0, sec=0):
    """adoytoymd(year, doy, hour, min, sec) -> string

Convert an array time with a day-of-year to a year-month-day time string.  The
hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_doy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    (mon, day) = _to_md[leap][doy]

    return '%04d%02d%02d%02d%02d%02d' % (year, mon, day, hour, min, sec)

def aymdtoadoy(year, mon, day, hour=0, min=0, sec=0):
    """aymdtoadoy(year, mon, day, hour, min, sec) -> (year, doy, hour, min, sec)

Convert an array time with a month and day to an array time with a day-of-year.
The hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    doy = _to_doy[leap][mon][day]

    return (year, doy, hour, min, sec)

def aymdtocdoy(year, mon, day, hour=0, min=0, sec=0):
    """aymdtocdoy(year, mon, day, hour, min, sec) -> string

Convert an array time with a month and day to a standard CCSDS day-of-year time
string.  The hour, minute and second parameters are optional.  All input
parameters must be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    doy = _to_doy[leap][mon][day]

    return '%04d-%03dT%02d:%02d:%02d' % (year, doy, hour, min, sec)

def aymdtocymd(year, mon, day, hour=0, min=0, sec=0):
    """aymdtocymd(year, mon, day, hour, min, sec) -> string

Convert an array time with a month and day to a standard CCSDS month and day
time string.  The hour, minute and second parameters are optional.  All input
parameters must be of type int."""

    #
    # validate input values
    #
    try:
	_val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return '%04d-%02d-%02dT%02d:%02d:%02d' % (year, mon, day, hour, min, sec)

def aymdtodoy(year, mon, day, hour=0, min=0, sec=0):
    """aymdtodoy(year, mon, day, hour, min, sec) -> string

Convert an array time with a month and day to a time string with a day-of-year.
The hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    doy = _to_doy[leap][mon][day]

    return '%04d%03d%02d%02d%02d' % (year, doy, hour, min, sec)

def aymdtomjd(year, mon, day, hour=0, min=0, sec=0):
    """aymdtomjd(year, doy, hour, min, sec) -> mjd

Convert an array time with a month and day to the Modified Julian Day (i.e.,
fractional days since Midnight, Nov 17, 1858).  The hour, minute and second
parameters are optional.  All input parameters must be of type int."""

    #
    # validate input values
    #
    try:
	leap = _val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    doy = _to_doy[leap][mon][day]
    uet = _doy_to_uet(year, doy, hour, min, sec)

    return _uet_to_mjd(uet)

def aymdtouet(year, mon, day, hour=0, min=0, sec=0):
    """aymdtouet(year, mon, day, hour, min, sec) -> uet

Convert an array time with a month and day the time in seconds since 1970
(UNIX epoch).  The hour, minute and second parameters are optional.  All
input parameters must be of type int.  This function returns a long int if
the result does not fit in an int."""

    #
    # validate input values
    #
    try:
	leap = _val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    doy = _to_doy[leap][mon][day]

    return _doy_to_uet(year, doy, hour, min, sec)

def aymdtoymd(year, mon, day, hour=0, min=0, sec=0):
    """aymdtoymd(year, mon, day, hour, min, sec) -> string

Convert an array time with a month and day to a time string with a month and day.
The hour, minute and second parameters are optional.  All input parameters must
be of type int."""

    #
    # validate input values
    #
    try:
	_val_ymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return '%04d%02d%02d%02d%02d%02d' % (year, mon, day, hour, min, sec)

def cdoytoadoy(str):
    """cdoytoadoy(str) -> (year, doy, hour, min, sec)

Convert a legal CCSDS time string with the date expressed as a day-of-year
into an array of values with the date expressed as a day-of-year."""

    if (type(str) is not types.StringType):
	raise TypeError, 'parameter is not a string type'

    try:
	if (len(str) >= 8) and (str[4:5] == '-'):
	    year = int(str[0:4])
	    doy = int(str[5:8])
	    if (len(str) == 8):
		hour = 0
		min = 0
		sec = 0
	    elif (len(str) >= 11) and (str[8:9] == 'T'):
		hour = int(str[9:11])
		if (len(str) == 11):
		    min = 0
		    sec = 0
		elif (len(str) >= 14) and (str[11:12] == ':'):
		    min = int(str[12:14])
		    if (len(str) == 14):
			sec = 0
		    elif (len(str) == 17) and (str[14:15] == ':'):
			sec = int(str[15:17])
		    else:
			raise ValueError
		else:
		    raise ValueError
	    else:
		raise ValueError
	else:
	    raise ValueError
	_val_doy(year, doy, hour, min, sec)
    except ValueError:
	raise ValueError, 'illegal CCSDS DOY string (' + str + ')'

    return (year, doy, hour, min, sec)

def cdoytoaymd(str):
    """cdoytoaymd(str) -> (year, mon, day, hour, min, sec)

Convert a legal CCSDS time string with the date expressed as a day-of-year
into an array of values with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	aymd = adoytoaymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return aymd

def cdoytocymd(str):
    """cdoytocymd(str) -> string

Convert a legal CCSDS time string with the date expressed as a day-of-year
to a CCSDS time string with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	cymd = adoytocymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def cdoytodoy(str):
    """cdoytodoy(str) -> string

Convert a legal CCSDS time string with the date expressed as a day-of-year
to a simple time string with the date expressed as a day-of-year."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	doy = adoytodoy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return doy

def cdoytomjd(str):
    """cdoytouet(str) -> uet

Convert a legal CCSDS time string with the date expressed as a day-of-year
to the Modified Julian Day (i.e., fractional days since Midnight, Nov 17,
1858)."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	uet = adoytomjd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def cdoytouet(str):
    """cdoytouet(str) -> uet

Convert a legal CCSDS time string with the date expressed as a day-of-year
to the time in seconds since 1970 (UNIX epoch)."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	uet = adoytouet(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def cdoytoymd(str):
    """cdoytoymd(str) -> string

Convert a legal CCSDS time string with the date expressed as a day-of-year
to a simple time string with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = cdoytoadoy(str)
	ymd = adoytoymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return ymd

def cymdtoadoy(str):
    """cymdtoadoy(str) -> (year, doy, hour, min, sec)

Convert a legal CCSDS time string with the date expressed as a month and day
into an array of values with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	adoy = aymdtoadoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return adoy

def cymdtoaymd(str):
    """cymdtoaymd(str) -> (year, mon, day, hour, min, sec)

Convert a legal CCSDS time string with the date expressed as a month and day
into an array of values with the date expressed as a month and day"""

    if (type(str) is not types.StringType):
	raise TypeError, 'parameter is not a string type'

    try:
	if (len(str) >= 10) and (str[4:5] == '-') and (str[7:8] == '-'):
	    year = int(str[0:4])
	    mon = int(str[5:7])
	    day = int(str[8:10])
	    if (len(str) == 10):
		hour = 0
		min = 0
		sec = 0
	    elif (len(str) >= 13) and (str[10:11] == 'T'):
		hour = int(str[11:13])
		if (len(str) == 13):
		    min = 0
		    sec = 0
		elif (len(str) >= 16) and (str[13:14] == ':'):
		    min = int(str[14:16])
		    if (len(str) == 16):
			sec = 0
		    elif (len(str) == 19) and (str[16:17] == ':'):
			sec = int(str[17:19])
		    else:
			raise ValueError
		else:
		    raise ValueError
	    else:
		raise ValueError
	else:
	    raise ValueError
	_val_ymd(year, mon, day, hour, min, sec)
    except ValueError:
	raise ValueError, 'illegal CCSDS YMD string (' + str + ')'

    return (year, mon, day, hour, min, sec)

def cymdtocdoy(str):
    """cymdtocdoy(str) -> string

Convert a legal CCSDS time string with the date expressed as a month and day
to a CCSDS time string with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	cdoy = aymdtocdoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cdoy

def cymdtodoy(str):
    """cymdtodoy(str) -> string

Convert a legal CCSDS time string with the date expressed as a month and day
to a simple time string with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	doy = aymdtodoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return doy

def cymdtomjd(str):
    """cymdtomjd(str) -> mjd

Convert a legal CCSDS time string with the date expressed as a month and day
to the Modified Julian Day (i.e., fractional days since Midnight, Nov 17,
1858)."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	mjd = aymdtomjd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return mjd

def cymdtouet(str):
    """cymdtouet(str) -> uet

Convert a legal CCSDS time string with the date expressed as a month and day
to the time in seconds since 1970 (UNIX epoch)."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	uet = aymdtouet(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def cymdtoymd(str):
    """cymdtoymd(str) -> string

Convert a legal CCSDS time string with the date expressed as a month and day
to a simple time string with the date expressed as a month and day."""

    try:
	(year, mon, day, hour, min, sec) = cymdtoaymd(str)
	ymd = aymdtoymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return ymd

def doytoadoy(str):
    """doytoadoy(str) -> (year, doy, hour, min, sec)

Convert a legal simple time string with the date expressed as a day-of-year
into an array of values with the date expressed as a day-of-year."""

    if (type(str) is not types.StringType):
	raise TypeError, 'parameter is not a string type'

    try:
	if (len(str) >= 7):
	    year = int(str[0:4])
	    doy = int(str[4:7])
	    if (len(str) == 7):
		hour = 0
		min = 0
		sec = 0
	    elif (len(str) >= 9):
		hour = int(str[7:9])
		if (len(str) == 9):
		    min = 0
		    sec = 0
		elif (len(str) >= 11):
		    min = int(str[9:11])
		    if (len(str) == 11):
			sec = 0
		    elif (len(str) == 13):
			sec = int(str[11:13])
		    else:
			raise ValueError
		else:
		    raise ValueError
	    else:
		raise ValueError
	else:
	    raise ValueError
	_val_doy(year, doy, hour, min, sec)
    except ValueError:
	raise ValueError, 'illegal DOY string (' + str + ')'

    return (year, doy, hour, min, sec)

def doytoaymd(str):
    """doytoaymd(str) -> (year, mon, day, hour, min, sec)

Convert a legal simple time string with the date expressed as a day-of-year
into an array of values with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	aymd = adoytoaymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return aymd

def doytocdoy(str):
    """doytocdoy(str) -> string

Convert a legal simple time string with the date expressed as a day-of-year
to a CCSDS time string with the date expressed as a day-of-year."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	cdoy = adoytocdoy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cdoy

def doytocymd(str):
    """doytocymd(str) -> string

Convert a legal simple time string with the date expressed as a day-of-year
to a CCSDS time string with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	cymd = adoytocymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def doytomjd(str):
    """doytouet(str) -> uet

Convert a legal simple time string with the date expressed as a day-of-year
to the Modified Julian Day (i.e., fractional days since Midnight, Nov 17,
1858)."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	uet = adoytomjd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def doytouet(str):
    """doytouet(str) -> uet

Convert a legal simple time string with the date expressed as a day-of-year
to the time in seconds since 1970 (UNIX epoch)."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	uet = adoytouet(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def doytoymd(str):
    """doytoymd(str) -> string

Convert a legal simple time string with the date expressed as a day-of-year
to a simple time string with the date expressed as a month and day."""

    try:
	(year, doy, hour, min, sec) = doytoadoy(str)
	ymd = adoytoymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return ymd

def gpstoadoy(week, dow=0, sec=0):
    raise NotImplementedError

def gpstoaymd(week, dow=0, sec=0):
    raise NotImplementedError

def gpstocdoy(week, dow=0, sec=0):
    raise NotImplementedError

def gpstocymd(week, dow=0, sec=0):
    """gpstocymd(week, dow=0, sec=0) -> string

Convert an array time with a GPS week, day-of-week, and seconds-of-day to
a CCSDS time with a month and day.  The day-of-week and seconds parameters
are optional.  All input parameters must be of type int."""

    try:
	uet = gpstouet(week, dow, sec)
	cymd = uettocymd(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def gpstodoy(week, dow=0, sec=0):
    raise NotImplementedError

def gpstomjd(week, dow=0, sec=0):
    raise NotImplementedError

def gpstouet(week, dow=0, sec=0):
    """gpstouet(week, dow, sec) -> uet

Convert an array time with a GPS week, day-of-week, and seconds-of-day to the
time in seconds since 1970 (UNIX epoch).  The day-of-week and seconds
parameters are optional.  All input parameters must be of type int.  This
function returns a long int if the result does not fit in an int."""

    #
    # validate input values
    #
    try:
	_val_gps(week, dow, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    #
    # return int if possible, otherwise use long
    #
    try:
	uet = (((week * 7) + dow) + 3657) * 86400 + sec
    except:
	uet = (((week * 7) + dow) + 3657) * 86400L + sec
    return uet

def gpstoymd(week, dow=0, sec=0):
    raise NotImplementedError

def mjdtoadoy(mjd):
    """mjdtoadoy(mjd) -> (year, doy, hour, min, sec)

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to an array time with a day-of-year.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	adoy = uettoadoy(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return adoy

def mjdtoaymd(mjd):
    """mjdtoaymd(mjd) -> (year, mon, day, hour, min, sec)

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to an array time with a month and day.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	aymd = uettoaymd(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return aymd

def mjdtocdoy(mjd):
    """mjdtocdoy(mjd) -> string

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to a CCSDS time with a day-of-year.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	cdoy = uettocdoy(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cdoy

def mjdtocymd(mjd):
    """mjdtocymd(mjd) -> string

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to a CCSDS time with a month and day.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	cymd = uettocymd(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def mjdtodoy(mjd):
    """mjdtodoy(mjd) -> string

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to a simple time with a day-of-year.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	doy = uettodoy(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return doy

def mjdtouet(mjd):
    """mjdtouet(mjd) -> uet

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to the time in seconds since 1970 (UNIX epoch).  The input time
may be a float, int or long int but must evaluate to a date between 1970
and 2100."""

    if type(mjd) is types.FloatType:
	if (mjd < 40587.0) or (mjd >= 88069.0):
	    raise ValueError, 'mjd (%f) is out of range' % mjd
    elif type(mjd) is types.IntType:
	if (mjd < 40587) or (mjd >= 88069):
	    raise ValueError, 'mjd (%d) is out of range' % mjd
    elif type(mjd) is types.LongType:
	if (mjd < 40587L) or (mjd >= 88069L):
	    raise ValueError, 'mjd (%d) is out of range' % mjd
    else:
	raise TypeError, 'mjd is not type float, int or long int'

    try:
	uet = int(86400 * (mjd - 40587) + 0.5)
    except:
	uet = long(86400L * (mjd - 40587) + 0.5)

    return uet

def mjdtoymd(mjd):
    """mjdtoymd(mjd) -> string

Convert the Modified Julian Day (i.e., fractional days since Midnight,
Nov 17, 1858) to a simple time with a month and day.  The input time may be a
float, int or long int but must evaluate to a date between 1970 and 2100."""

    try:
	uet = mjdtouet(mjd)
	ymd = uettoymd(uet)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return ymd

def uettoadoy(uet):
    """uettoadoy(uet) -> (year, doy, hour, min, sec)

Convert the time in seconds since 1970 (UNIX epoch) to an array time with the
date expressed as a day-of-year.  The input time may be an int or a long int
but must be positive and evaluate to a date before 2100."""

    if type(uet) is types.IntType:
	if uet < 0:
	    raise ValueError, 'uet (%d) is out of range' % uet
    elif type(uet) is types.LongType:
	if uet < 0L:
	    raise ValueError, 'uet (%d) is out of range' % uet
	elif uet > 4102444799L:
	    raise ValueError, 'uet (%d) is out of range' % uet
    else:
	raise TypeError, 'uet is not type int or long int'

    sec = int(uet % 60)
    uet = uet / 60
    min = int(uet % 60)
    uet = uet / 60
    hour = int(uet % 24)
    uet = int(uet / 24)

    #
    # calculate days in blocks of four years
    #
    doy = (uet + 365) % 1461
    year = 1969 + (uet + 365) / 1461 * 4
    if doy == 1460:
	year = year + 3
	doy = 366
    else:
	year = year + doy / 365
	doy = (doy % 365) + 1

    return (year, doy, hour, min, sec)

def uettoaymd(uet):
    """uettoaymd(uet) -> (year, doy, hour, min, sec)

Convert the time in seconds since 1970 (UNIX epoch) to an array time with the
date expressed as a month and day.  The input time may be an int or a long int
but must be positive and evaluate to a date before 2100."""

    try:
	(year, doy, hour, min, sec) = uettoadoy(uet)
	aymd = adoytoaymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return aymd

def uettocdoy(uet):
    """uettocdoy(uet) -> string

Convert the time in seconds since 1970 (UNIX epoch) to a CCSDS time string
with the date expressed as a month and day.  The input time may be an int or
a long int but must be positive and evaluate to a date before 2100."""

    try:
	(year, doy, hour, min, sec) = uettoadoy(uet)
	cdoy = adoytocdoy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cdoy

def uettocymd(uet):
    """uettocymd(uet) -> string

Convert the time in seconds since 1970 (UNIX epoch) to a CCSDS time string
with the date expressed as a day-of-year.  The input time may be an int or a
long int but must be positive and evaluate to a date before 2100."""

    try:
	(year, doy, hour, min, sec) = uettoadoy(uet)
	cymd = adoytocymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def uettodoy(uet):
    """uettodoy(uet) -> string

Convert the time in seconds since 1970 (UNIX epoch) to a simple time string
with the date expressed as a month and day.  The input time may be an int or
a long int but must be positive and evaluate to a date before 2100."""

    try:
	(year, doy, hour, min, sec) = uettoadoy(uet)
	doy = adoytodoy(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return doy

def uettomjd(uet):
    """uettomjd(uet) -> mjd

Convert the time in seconds since 1970 (UNIX epoch) to the Modified Julian
Day (i.e., fractional days since Midnight, Nov 17, 1858).  The input time
may be an int or a long int but must be positive and evaluate to a date
before 2100."""

    if type(uet) is types.IntType:
	if uet < 0:
	    raise ValueError, 'uet (%d) is out of range' % uet
    elif type(uet) is types.LongType:
	if uet < 0L:
	    raise ValueError, 'uet (%d) is out of range' % uet
	elif uet > 4102444799L:
	    raise ValueError, 'uet (%d) is out of range' % uet
    else:
	raise TypeError, 'uet is not type int or long int'

    return _uet_to_mjd(uet)

def uettoymd(uet):
    """uettoymd(uet) -> string

Convert the time in seconds since 1970 (UNIX epoch) to a simple time string
with the date expressed as a day-of-year.  The input time may be an int or a
long int but must be positive and evaluate to a date before 2100."""

    try:
	(year, doy, hour, min, sec) = uettoadoy(uet)
	ymd = adoytoymd(year, doy, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return ymd

def ymdtoadoy(str):
    """ymdtoadoy(str) -> (year, doy, hour, min, sec)

Convert a legal simple time string with the date expressed as a month and day
into an array of values with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	adoy = aymdtoadoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return adoy

def ymdtoaymd(str):
    """ymdtoaymd(str) -> (year, mon, day, hour, min, sec)

Convert a legal simple time string with the date expressed as a month and day
into an array of values with the date expressed as a month and day"""

    if (type(str) is not types.StringType):
	raise TypeError, 'parameter is not a string type'

    try:
	if (len(str) >= 8):
	    year = int(str[0:4])
	    mon = int(str[4:6])
	    day = int(str[6:8])
	    if (len(str) == 8):
		hour = 0
		min = 0
		sec = 0
	    elif (len(str) >= 10):
		hour = int(str[8:10])
		if (len(str) == 10):
		    min = 0
		    sec = 0
		elif (len(str) >= 12):
		    min = int(str[10:12])
		    if (len(str) == 12):
			sec = 0
		    elif (len(str) == 14):
			sec = int(str[12:14])
		    else:
			raise ValueError
		else:
		    raise ValueError
	    else:
		raise ValueError
	else:
	    raise ValueError
	_val_ymd(year, mon, day, hour, min, sec)
    except ValueError:
	raise ValueError, 'illegal YMD string (' + str + ')'

    return (year, mon, day, hour, min, sec)

def ymdtocdoy(str):
    """ymdtocdoy(str) -> string

Convert a legal simple time string with the date expressed as a month and day
to a CCSDS time string with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	cdoy = aymdtocdoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cdoy

def ymdtocymd(str):
    """ymdtocymd(str) -> string

Convert a legal simple time string with the date expressed as a month and day
to a CCSDS time string with the date expressed as a month and day."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	cymd = aymdtocymd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return cymd

def ymdtodoy(str):
    """ymdtodoy(str) -> string

Convert a legal simple time string with the date expressed as a month and day
to a simple time string with the date expressed as a day-of-year."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	doy = aymdtodoy(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return doy

def ymdtomjd(str):
    """ymdtomjd(str) -> mjd

Convert a legal simple time string with the date expressed as a month and day
to the Modified Julian Day (i.e., fractional days since Midnight, Nov 17,
1858)."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	mjd = aymdtomjd(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return mjd

def ymdtouet(str):
    """ymdtouet(str) -> uet

Convert a legal simple time string with the date expressed as a month and day
to the time in seconds since 1970 (UNIX epoch)."""

    try:
	(year, mon, day, hour, min, sec) = ymdtoaymd(str)
	uet = aymdtouet(year, mon, day, hour, min, sec)
    except TypeError, e:
	raise TypeError, e.args[0]
    except ValueError, e:
	raise ValueError, e.args[0]

    return uet

def anytoadoy():
    raise NotImplementedError

def anytoaymd():
    raise NotImplementedError

def anytocdoy():
    raise NotImplementedError

def anytocymd():
    raise NotImplementedError

def anytodoy():
    raise NotImplementedError

def anytomjd():
    raise NotImplementedError

def anytouet():
    raise NotImplementedError

def anytoymd():
    raise NotImplementedError

def addtoadoy():
    raise NotImplementedError

def addtoaymd():
    raise NotImplementedError

def addtocdoy():
    raise NotImplementedError

def addtocymd():
    raise NotImplementedError

def addtodoy():
    raise NotImplementedError

def addtoymd():
    raise NotImplementedError

def diffadoy():
    raise NotImplementedError

def diffaymd():
    raise NotImplementedError

def diffcdoy():
    raise NotImplementedError

def diffcymd():
    raise NotImplementedError

def diffdoy():
    raise NotImplementedError

def diffymd():
    raise NotImplementedError

def doytoweek():
    raise NotImplementedError

def cdoytofmt():
    raise NotImplementedError

def getyear():
    raise NotImplementedError

def hmstosec():
    raise NotImplementedError

def isleap(year):
    """isleap(year) -> boolean

Return 1 if the year is a leap year, otherwise return 0."""

    if (type(year) is not types.IntType):
	raise TypeError, 'year is not type int'
    if ((year < 1970) or (year > 2099)):
	raise ValueError, 'year (%d) is out of range' % year
    if ((year % 4) == 0):
	return 1
    else:
	return 0

def lsstoadoy():
    raise NotImplementedError

def lsstoaymd():
    raise NotImplementedError

def lsstocdoy():
    raise NotImplementedError

def lsstocymd():
    raise NotImplementedError

def lsstodoy():
    raise NotImplementedError

def lsstomjd():
    raise NotImplementedError

def lsstouet():
    raise NotImplementedError

def lsstoymd():
    raise NotImplementedError

def sectohms():
    raise NotImplementedError

def uettofmt():
    raise NotImplementedError

def weekofadoy():
    raise NotImplementedError

def weekofaymd():
    raise NotImplementedError

def weekofcdoy():
    raise NotImplementedError

def weekofcymd():
    raise NotImplementedError

def weekofdoy():
    raise NotImplementedError

def weekofmjd():
    raise NotImplementedError

def weekofuet():
    raise NotImplementedError

def weekofymd():
    raise NotImplementedError

def weektodoy():
    raise NotImplementedError

def yr2toyr4(year):
    """yr2toyr4(year2) -> year4

Convert a two-digit year to a four-digit year.  The window is from 1995
through 2094."""

    if (type(year) is not types.IntType):
	raise TypeError, 'year is not type int'
    if ((year < 0) or (year > 99)):
	raise ValueError, 'two-digit year (%d) is out of range' % year
    if year >= 95:
	return 1900 + year
    else:
	return 2000 + year

def yr4toyr2(year):
    """yr4toyr2(year4) -> year2

Convert a four-digit year to a two-digit year.  The window is from 1995
through 2094."""

    if (type(year) is not types.IntType):
	raise TypeError, 'year is not type int'
    if ((year < 1995) or (year > 2094)):
	raise ValueError, 'four-digit year (%d) is out of range' % year
    return year % 100

#
# local variable and constant definitions
#

#
# generate a table to convert doy to ymd
#
#	(mon, day) = _to_md[leap][doy]
#	doy = _to_doy[leap][mon][day]
#
# generate a table of the last day of each month
#
#	last_day = _last_day[leap][mon]
#
_ndays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_ldays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_to_md = [[None], [None]]
_to_doy = [[None], [None]]
_last_day = [[None], [None]]
for _i in range(12):
    _to_doy[0].append([None])
    _to_doy[1].append([None])
    _last_day[0].append(_ndays[_i])
    _last_day[1].append(_ldays[_i])
    for _j in range(_ndays[_i]):
	_to_md[0].append((_i + 1, _j + 1))
	_to_doy[0][_i + 1].append(len(_to_md[0]) - 1)
    for _j in range(_ldays[_i]):
	_to_md[1].append((_i + 1, _j + 1))
	_to_doy[1][_i + 1].append(len(_to_md[1]) - 1)

#
# internal function definitions
#

def _val_doy(year, doy, hour, min, sec):
    #
    # validate input values
    #
    try:
	leap = isleap(year)
    except TypeError:
	raise TypeError, 'year is not type int'
    except ValueError:
	raise ValueError, 'year (%d) is out of range' % year

    if (type(doy) is not types.IntType):
	raise TypeError, 'doy is not type int'
    if ((doy < 1) or (doy > 365 + leap)):
	raise ValueError, 'doy (%d) is out of range' % doy

    if (type(hour) is not types.IntType):
	raise TypeError, 'hour is not type int'
    if ((hour < 0) or (hour > 23)):
	raise ValueError, 'hour (%d) is out of range' % hour

    if (type(min) is not types.IntType):
	raise TypeError, 'min is not type int'
    if ((min < 0) or (min > 59)):
	raise ValueError, 'min (%d) is out of range' % min

    if (type(sec) is not types.IntType):
	raise TypeError, 'sec is not type int'
    if ((sec < 0) or (sec > 59)):
	raise ValueError, 'sec (%d) is out of range' % sec

    return leap

def _val_ymd(year, mon, day, hour, min, sec):
    #
    # validate input values
    #
    try:
	leap = isleap(year)
    except TypeError:
	raise TypeError, 'year is not type int'
    except ValueError:
	raise ValueError, 'year (%d) is out of range' % year

    if (type(mon) is not types.IntType):
	raise TypeError, 'mon is not type int'
    if ((mon < 1) or (mon > 12)):
	raise ValueError, 'mon (%d) is out of range' % mon

    if (type(day) is not types.IntType):
	raise TypeError, 'day is not type int'
    if ((day < 1) or (day > _last_day[leap][mon])):
	raise ValueError, 'day (%d) is out of range' % day

    if (type(hour) is not types.IntType):
	raise TypeError, 'hour is not type int'
    if ((hour < 0) or (hour > 23)):
	raise ValueError, 'hour (%d) is out of range' % hour

    if (type(min) is not types.IntType):
	raise TypeError, 'min is not type int'
    if ((min < 0) or (min > 59)):
	raise ValueError, 'min (%d) is out of range' % min

    if (type(sec) is not types.IntType):
	raise TypeError, 'sec is not type int'
    if ((sec < 0) or (sec > 59)):
	raise ValueError, 'sec (%d) is out of range' % sec

    return leap

def _val_gps(week, dow, sec):
    #
    # validate input values
    #
    if (type(week) is not types.IntType):
	raise TypeError, 'week is not type int'
    if (week < 0):
	raise ValueError, 'week (%d) is out of range' % week

    if (type(dow) is not types.IntType):
	raise TypeError, 'dow is not type int'
    if ((dow < 0) or (dow > 6)):
	raise ValueError, 'dow (%d) is out of range' % dow

    if (type(sec) is not types.IntType):
	raise TypeError, 'sec is not type int'
    if ((sec < 0) or (sec > 86399)):
	raise ValueError, 'sec (%d) is out of range' % sec

    return

def _doy_to_uet(year, doy, hour, min, sec):
    #
    # calculate days in blocks of four years
    #
    uet = ((((year - 1969) / 4) * 1461) + (((year - 1969) % 4) * 365)
	+ doy - 366)

    #
    # return int if possible, otherwise use long
    #
    try:
	uet = uet * 86400 + hour * 3600 + min * 60 + sec
    except:
	uet = uet * 86400L + hour * 3600 + min * 60 + sec
    return uet

def _uet_to_mjd(uet):
    #
    # days from MJD epoch (1858-11-18) to current Unix epoch (1970-01-01)
    # is 40587
    #
    return (uet / 86400.0) + 40587
