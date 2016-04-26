#!/usr/bin/env python
#
#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.

"""
26 Nov 2014

Script to run pergola from the command line using isatab format
"""

sp = " "

from pergola import parsers
from pergola import isatab_parser
from pergola  import intervals
from pergola  import mapping
# from scripts import pergola_rules
from argparse import ArgumentParser, ArgumentTypeError
from sys      import stderr, exit
from os import path

# from bcbio import isatab
import pergola_rules


# from urllib import urlretrieve, URLopener
from urllib2 import urlopen, URLError, HTTPError

home_dir = path.expanduser('~')
path_pergola = path.join(home_dir,".pergola/projects")

url = "https://raw.githubusercontent.com/cbcrg/pergola/master/data/feeding_beh_files/20120502_FDF_CRG_hab_DevW1_W2_filt_c1.csv"
# url = "/users/cn/jespinosa/Desktop/SB_PhD_list.txt"

# check_assay_pointer(url)
      

def main():

    parser_isatab = ArgumentParser(parents=[parsers.parent_parser])        
    parser_isatab.add_argument('-ft', '--file_tab', required=False, metavar="FILE_TAG", help='Tag for file field in isatab')

    args = parser_isatab.parse_args()
    
    print >> stderr, "@@@Pergola_isatab.py: Input file: %s" % args.input 
    print >> stderr, "@@@Pergola_isatab.py: Configuration file: %s" % args.mapping_file
    print >> stderr, "@@@Pergola_isatab.py: Selected tracks are: ", args.tracks
    
    # I have to check whether when a isatab folder is given if it is actually a folder or a file
    # difference with -i
    if not path.isdir(args.input):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    # It might be interesting to check inside the function whether files are url or in path
    dict_files = isatab_parser.parse_isatab_assays (args.input)
    print dict_files
    
    # First try with files in local then with url
    for key in dict_files:
        pointer_file = dict_files[key]
#         print "key %s -----value %s"% (key, dict_files[key]) #del or #perm
#         print ">>>>>>>>>>>>>>>>>>>>>pointer to file is:", pointer_file #del or #perm
        
        # Tengo que relacionar de alguna manera cual es el assay de donde tiene que sacar los archivos
        #Probar varios isatab files 
        
        file_path = isatab_parser.check_assay_pointer(pointer_file, download_path=path_pergola) 
#         print "File name is::::::::::::::::::::::::::%s   \n" % file_path #del or #perm
        
#         data_types_list=args.data_types_list #del
        pergola_rules.main(path=file_path, map_file_path=args.mapping_file,
                           sel_tracks=args.tracks, list=args.list, range=args.range,
                           track_actions=args.track_actions, data_types_list=args.data_types_list,
                           data_types_actions=args.data_types_actions, write_format=args.format,
                           relative_coord=args.relative_coord, intervals_gen=args.intervals_gen,                        
                           multiply_f=args.multiply_intervals, fields2read=args.fields_read, 
                           window_size=args.window_size)
        
        print >> stderr, "@@@Pergola_isatab.py: execution finished correctly" 
#         exit ("Going out to see what do I have here")#del
#It might be interesting to implement a append option

if __name__ == '__main__':
    exit(main())