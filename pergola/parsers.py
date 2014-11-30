"""
=========================
Module: pergola.parsers
=========================

.. module:: parsers

This module provides the way to read scripts options provided by pergola library.


"""

from argparse import ArgumentParser
from re       import match

_dt_act_options = ['all', 'one_per_channel']
_tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even']

def parse_num_range(string):
    """ 
    This function generate a numeric range from a string containing the boundaries
    From 1-4 generates a string  
    
    :param tracks: :py:func:`set` of tracks to which track_action should be applied set([1,2])
    :param delimiter: :py:func:`str` option to join tracks (join_all, split_all, join_odd, join_evens)
            
    :return: :py:func:`set` with all the numbers in range as strings
    
    """
    
    m = match(r'(\d+)(?:-(\d+))?$', string)

    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    list_range=list(range(int(start,10), int(end,10)+1))
    set_range=set(['{0}'.format(t) for t in list_range]) #str because track can be set in the form of track_1 for instance
    
    return set_range

def read_track_actions (tracks, track_action = "split_all"):
    """ 
    Read track actions and returns a set with the tracks to be joined
    
    :param tracks: :py:func:`set` of tracks to which track_action should be applied set([1,2])
    :param track_action: :py:func:`str` option to join tracks (join_all, split_all, join_odd, join_evens)
    
    :return: :py:func:`set` of tracks to be joined
     
    """
    
    if track_action not in _tr_act_options:
        raise ValueError("Track_action \'%s\' not allowed. Possible values are %s"%(track_action,', '.join(['{}'.format(m) for m in _tr_act_options])))
    
    tracks2merge = ""
    
    if track_action == "join_all":
        tracks2merge = tracks
    elif track_action == 'join_odd':
        tracks2merge = set([t for t in tracks if int(t) % 2])
    elif track_action == 'join_even':
        tracks2merge = set([t for t in tracks if not int(t) % 2])
    else:
        tracks2merge = ""
        
    print >> stderr,"Tracks to merge are: ", ",".join("'{0}'".format(t) for t in tracks2merge)
       
    if not tracks2merge:
        print >> stderr,("No track action applied as track actions \'%s\' can not be applied to list of tracks provided \'%s\'"%(track_action, " ".join(tracks)))
        
    return (tracks2merge)


parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data', add_help=False)
parser.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')
parser.add_argument('-o', '--ontology_file', required=True, metavar="ONTOLOGY_FILE",
                    help='File with the ontology between fields in behavioral file' + \
                    'and genome browser grammar')
parser.add_argument('-t', '--tracks', required=False, metavar="TRACKS", type=int, nargs='+', 
                    help='List of selected tracks')
parser.add_argument('-l','--list', required=False, metavar="LIST_OF_TRACKS", type=str, nargs='+',
                    help='Numeric list of tracks to be joined in a single genomic like file')### string allowed as some tracks could be named as: track_1, track2....
parser.add_argument('-r', '--range', required=False, type=parse_num_range,
                    help='Numeric range of tracks to be joined in a single genomic like file')
parser.add_argument('-a', '--track_actions', required=False, choices=_tr_act_options,
                    help='Option of action with tracks selected, split_all, join_all,' + \
                         ' join_odd, join_even, join_range or join_list')
parser.add_argument('-d', '--dataTypes_actions', required=False, choices=_dt_act_options,
                    help='Unique values of dataTypes field should be dumped on' + \
                         ' different data structures or not')
parser.add_argument('-f', '--format', required=False, type=str, 
                    help='Write file output format (bed or bedGraph)')
parser.add_argument('-e', '--relative_coord', required=False, action='store_true', 
                    default=False, help='Sets first timepoint' \
                    ' to 0 and make all the others relative to this timepoint')
parser.add_argument('-n', '--intervals_gen', required=False, action='store_true', 
                    default=False, help='Set startChrom and endChrom from just a timepoint in the file' \
                                        'using field set as startChrom')
parser.add_argument('-m', '--multiply_factor', metavar='N', type=int, required=False,
                    help='Multiplies value in dataValue by the given value')
parser.add_argument('-s', '--fields_read', metavar='FIELDS2READ', type=str, nargs='+',
                    help='List of fields to read from input file')

