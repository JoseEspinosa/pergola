"""
======================
Module: pergola.tracks
======================

.. module:: tracks

This module  provides the structures to keep the data in genomic format.
It provides a generic class :class:`~pergola.tracks.GenomicContainer` which has 
the general attributes and methods shared by all the other subclasses. 

These subclasses provide special features for each type of data and are:
 
:py:class:`~pergola.tracks.Track` objects are generated by
:func:`pergola.intervals.IntData.read` and hold the parsed and manipulated
data as an iterator and the attributes generated when reading file 

:py:class:`~pergola.tracks.Bed` :class:`~pergola.tracks.GenomicContainer` class 
for Bed files.

:py:class:`~pergola.tracks.BedGraph` :class:`~pergola.tracks.GenomicContainer` class 
for BedGraph files.

"""

from os  import getcwd
from sys import stderr
from os.path import join
from operator import itemgetter
from itertools import groupby
from numpy import arange 

#Contains class and file extension
_dict_file = {'bed' : ('Bed', 'track_convert2bed', '.bed'),              
              'bedGraph': ('BedGraph', 'track_convert2bedGraph', '.bedGraph'),
              'txt': ('Track', '', '.txt')}

_black_gradient = ["226,226,226", "198,198,198", "170,170,170", "141,141,141", "113,113,113", "85,85,85", "56,56,56", "28,28,28", "0,0,0"]
_blue_gradient = ["229,229,254", "203,203,254", "178,178,254", "152,152,254", "127,127,254", "102,102,254", "76,76,173", "51,51,162", "0,0,128"]
_red_gradient = ["254,172,182", "254,153,162", "254,134,142", "254,115,121", "254,96,101", "254,77,81", "254,57,61", "254,38,40", "254,19,20"]
_green_gradient = ["203,254,203", "178,254,178", "152,254,152", "127,254,127", "102,254,102", "76,254,76", "51,254,51", "0,254,0", "25,115,25"]

_dict_colors = {
                'black' : _black_gradient,
                'blue' : _blue_gradient,
                'red' : _red_gradient,
                'green' : _green_gradient}

# _intervals = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 1, 1000] #del

class GenomicContainer(object):
    """
    This class provides the general attributes and methods shared by all the other
    subclasses that contain the data after being read :func:`pergola.intervals.IntData.read`
    or converted by :py:func:`pergola.tracks.Track.convert`

    .. attribute:: data
    
       Iterator yielding record of the genomic data
    
    .. attribute:: fields
    
       List of name of each of the fields contained in records of data
    
    .. attribute:: format
       
       Format to write file (extension) 
    
    .. attribute:: track
       
       String with the name of the track
    
    .. attribute:: range_values
       
       Range of values inside dataValue field
       
    ..
       Indicates the presence of a header.
       * `False` if there is no header. Fields should the be provided using fields param
       * `True` if the file have a header line with names. This names should match names in ontology_dict (default).
       
    :returns: GenomicContainer object
        
    """
    def __init__(self, data, fields=None, dataTypes=None, **kwargs):
        if isinstance(data,(tuple)):            
            data = iter(data)
        
        if not fields:
            raise ValueError("Must specify a 'fields' attribute for %s." % self.__str__())
        
        self.data = data
        self.fields = fields
        self.dataTypes = dataTypes     
        self.format = kwargs.get("format",'txt')
        self.track = kwargs.get('track', "1")
        self.range_values = kwargs.get('range_values', None)
        
    def __iter__(self):
        return self.data

    def next(self):
        """
        
        :returns: next item in iterator
         
        """
        return self.data.next()
    
    def save_track(self, mode="w", path=None, name_file=None, track_line=True, bed_label=False):
        """
        Save the data in a file of format set by *self.format* 
        
        :param "w" mode: :py:func:`str` Only implemented write 'w' (default). 
        
        :param None path: Path to create file, py:func:`str`. If None (default) the 
            file is dumped in the current working directory and prints a warning.  
        
        :param None track: Path to create file, py:func:`str`. If None (default) the 
            file is dumped in the current working directory and prints a warning.
            
        :param True track_line: If it is set to True includes the track_line 
        
        :param None name_file: :py:func: `str` to set name of output file
        
        :param False bed_label: Whether to include or not the labels of each interval, 
            default False in bed files
        
        :returns: Void
        
        
        """
        
        if not path: 
            pwd = getcwd()
        else:
            pwd = path
            
        print >> stderr, "No path selected, files dump into path: ", pwd 
                             
        if not(isinstance(self, GenomicContainer)):
            raise Exception("Not writable object, type not supported '%s'."%(type(self)))    
        
        try:
            file_ext = _dict_file.get(self.format)[2]      
        except KeyError:
            raise ValueError("File types not supported \'%s\'"%(self.format))
        
        if name_file is None:
            conc_dataTypes = self.dataTypes
            if isinstance(conc_dataTypes, set):
                conc_dataTypes="_".join(self.dataTypes)        
                        
            name_file = "tr_" + self.track + "_dt_" + conc_dataTypes + file_ext
        else:
            name_file = name_file + file_ext
            
        print >> stderr, "File %s generated" % name_file       

        track_file = open(join(pwd, name_file), mode)
                
        #Annotation track to set the genome browser interface
        annotation_track = ''
        
        if self.format == 'bed' and track_line:
            annotation_track = 'track type=' + self.format + " " + 'name=\"' +  self.track + "_" + self.dataTypes + '\"' + " " + 'description=\"' + self.track + " " + self.dataTypes + '\"' + " " + "visibility=2 itemRgb=\"On\" priority=20"
            track_file.write (annotation_track + "\n") 
        elif self.format == 'bedGraph' and track_line:
            annotation_track = 'track type=' + self.format + " " + 'name=\"' + self.track + "_" + self.dataTypes + '\"' + " " + 'description=\"' + self.track + "_" + self.dataTypes + '\"' + " " + 'visibility=full color=' + self.color_gradient[7] + ' altColor=' + self.color_gradient[8] + ' priority=20'        #             
            track_file.write (annotation_track + "\n")        
          
        for row in self.data: 
            
            if self.format == 'bed' and not bed_label:
                index_name = self.fields.index ('name') 
                empty_label = '""'
                row = [empty_label if (i == index_name) else (v) for (i, v) in enumerate(row)]
                
            track_file.write('\t'.join(str(v) for v in row))           
            track_file.write("\n")
                  
        track_file.close()
    
class Track(GenomicContainer):
    """
    This class is not commented
    
    inherits from :py:class:`GenomicContainer`
    """
    def __init__(self, data, fields=None, dataTypes=None, list_tracks=None, **kwargs):
        self.list_tracks = list_tracks
        self.list_tracks_filt = []
        self.list_data_types=dataTypes
        GenomicContainer.__init__(self, data, fields, dataTypes, **kwargs)

    def convert(self, mode='bed', range_color=None, **kwargs):
        """
        Calls function to convert data (as a list of tuples) into a dictionary of 
        the one or several object of class set by mode
        
        :param bed mode: class of the output objects returned set to `bed` by
            default
            
        :param range_color: :py:func:`list` with range of values to set colors 
            of bed file. If set modifies self.range_values
            
        :param tracks2remove: :py:func:`list` of tracks to remove from the dict_t
        
        :returns: dictionary containing object/s of the class set by mode 
        
        """
        kwargs['relative_coord'] = kwargs.get("relative_coord",False)     
        
        if mode not in _dict_file: 
            raise ValueError("Mode \'%s\' not available. Possible convert() modes are %s"%(mode,', '.join(['{}'.format(m) for m in _dict_file.keys()])))
        
        # User set values for bed file colors
        if range_color:
            if (len(range_color) != 2 or all(isinstance(n, int) for n in range_color)):
                raise ValueError ("Range color must be a list with two numeric values" \
                                  % (range_color))
        
            self.range_values = range_color

#         dict_tracks = (self._convert2single_track(self._read(**kwargs), mode, **kwargs)) #TODO
        dict_tracks = (self._convert2single_track(self.data, mode, **kwargs)) 
#         dict_tracks = (self._convert2single_track(self.data, mode, **kwargs)) #TODO
        
        return (dict_tracks)
        
    def _convert2single_track (self, data_tuples,  mode=None, **kwargs):
        """
        Split data (as a list of tuples) into one or several objects depending on options 
        selected. Each object will correspond to a track in the genome browser
        
        :param data_tuples: list of tuples containing data
        :param None mode: class of each single track that will be hold in dictionary
            
        :returns: dictionary of tracks
        
        """
           
        dict_split = {}
        
        ### Data is separated by track and dataTypes
        idx_fields2split = [self.fields.index("track"), self.fields.index("dataTypes")]
        data_tuples = sorted(data_tuples, key=itemgetter(*idx_fields2split))
        
        for key,group in groupby(data_tuples, itemgetter(*idx_fields2split)):
            if not dict_split.has_key(key[0]):
                dict_split [key[0]] = {}
            dict_split [key[0]][key[1]] = tuple(group)
        
        #Generate dictionary of original fields and color gradients
        color_restrictions = kwargs.get('color_restrictions', None)
        _dict_col_grad = dict()
        
        ### Tracks not set in tracks option are filtered out
        sel_tracks = []
        if not kwargs.get('tracks'):
            pass
        else:
            sel_tracks = map(str, kwargs.get("tracks",[]))
                   
        ### When any tracks are selected we consider that no track should be removed
        if sel_tracks != []:
            tracks2rm = self.list_tracks.difference(sel_tracks)           
            dict_split = self.remove (dict_split, tracks2rm)
            print >> stderr, "Removed tracks are:", ' '.join(tracks2rm)
         
        # Eventually I can eliminate tracks of not selected tracks
#         self.data = [y for y in data_tuples if y[0] in self.list_tracks]
        
        sel_data_types = []
        if not kwargs.get('data_types'):
            pass
        else:            
            sel_data_types = map(str, kwargs.get("data_types",[]))
        
        new_dict_split = {}    
        ### When any data_types are selected we consider that no data_types should be removed
        if sel_data_types  != []:
            data_types2rm = self.list_data_types.difference(sel_data_types)
            for track, track_dict in dict_split.items():    
                dict_data_type = self.remove (track_dict, data_types2rm)        
                new_dict_split [track] = dict_data_type
            print >> stderr, "Removed data types are:", ' '.join(data_types2rm)        
            
        
        if new_dict_split: 
            dict_split = new_dict_split
                
        d_track_merge = {} 
        
        ### If tracks_merge is set we combine tracks selected                 
        if not kwargs.get('tracks_merge'):
            d_track_merge = dict_split
        else:
#             tracks_merge = kwargs.get('tracks_merge',self.list_tracks)
            tracks_merge = kwargs.get('tracks_merge',self.list_tracks_filt)
#             if not all(tracks in self.list_tracks for tracks in tracks_merge):
            if not all(tracks in self.list_tracks_filt for tracks in tracks_merge):
                raise ValueError ("Tracks to merge: %s, are not in the track list: " % 
                                  ",".join("'{0}'".format(n) for n in tracks_merge), 
                                  ",".join("'{0}'".format(n) for n in self.list_tracks_filt))
            print >> stderr, ("Tracks that will be merged are: %s" %  " ".join(tracks_merge))
            
            d_track_merge = self.join_by_track(dict_split, tracks_merge)       
        
        d_dataTypes_merge = {}
        
        ### If set we join the dataTypes or natures
        if not kwargs.get('dataTypes_actions') or kwargs.get('dataTypes_actions') == 'one_per_channel':
            d_dataTypes_merge = d_track_merge
        elif kwargs.get('dataTypes_actions') == 'all':
            d_dataTypes_merge = self.join_by_dataType(d_track_merge, mode)
        
        if mode == 'bedGraph':     
            _dict_col_grad = assign_color (self.dataTypes, color_restrictions)
         
        track_dict = {}                        
   
        ### Generating track dict (output)                         
        window = kwargs.get("window", 300)
             
        ### Assigning data to output dictionary    
        for k, d in d_dataTypes_merge.items():
            if not isinstance(d,dict):
                raise ValueError ("The structure that holds the tracks should be a dictionary of dictionaries")
            
            for k_2, d_2 in d.items():
                if not k_2 in _dict_col_grad and mode == "bed":
                    _dict_col_grad[k_2] = ""
                
                track_dict[k,k_2] = globals()[_dict_file[mode][0]](getattr(self,_dict_file[mode][1])(d_2, True, window=window, color_restrictions=color_restrictions), track=k, dataTypes=k_2, range_values=self.range_values, color=_dict_col_grad[k_2])
                            
        return (track_dict)
    
    
    def remove (self, dict_t, tracks2remove):
        """
        Removes selected tracks from a dictionary of tracks that is the input of the function those that are 
        set by tracks2remove
        
        :param dict_t: py:func:`dict` dictionary containing one or more tracks, keys represent each 
            of these tracks
        :param tracks2remove: :py:func:`list` of tracks to remove from the dict_t
             
        :returns: dict_t dictionary, that contains the remaining tracks
        
        #TODO I can make this function more general as remove from dictionary it can be use outside
        # in fact I am using now it to remove data_types and not only tracks
        """
        for key in tracks2remove:
            key = str(key)
    
            dict_t.pop(key, None)
            
#             if key in self.list_tracks:        #OJO
#                 self.list_tracks.remove(key)
            
            if key in self.list_tracks_filt:        
                self.list_tracks_filt.remove(key)
            
#             if key in self.list_data_types:
#                 self.list_data_types.remove(key)
                    
        return (dict_t)
    
    def join_by_track(self, dict_t, tracks2join):  
        """
        Join tracks by track name or id 
        
        :param dict_t: py:func:`dict` containing one or more tracks, keys 
            represent each of these tracks
        :param tracks2join: :py:func:`list` of tracks to join in a single track
             
        :returns: d_track_merge dictionary that contains the joined tracks
        
        TODO What if I give to the function only some tracks to join, what happen
            to the remaining tracks
         
        """
        
        d_track_merge = {} 
        new_tracks = set()
        
        for key, nest_dict in dict_t.items():
            
            if key not in tracks2join: 
                print "Track not use because was not set when join_by_track is called: %s" % key
                continue
            
            if not d_track_merge.has_key('_'.join(tracks2join)):
                d_track_merge['_'.join(tracks2join)] = {}
                new_tracks.add('_'.join(tracks2join))
            
            for key_2, data in nest_dict.items():                            
                if not d_track_merge['_'.join(tracks2join)].has_key(key_2):
                    d_track_merge['_'.join(tracks2join)] [key_2]= data
                else:  
                    d_track_merge['_'.join(tracks2join)] [key_2] = d_track_merge['_'.join(tracks2join)] [key_2] + data

#         self.list_tracks = new_tracks
                   
        return (d_track_merge)
    
    
    def join_by_dataType (self, dict_d, mode):
        """
        Join tracks by dataType
        
        :param dict_d: py:func:`dict` containing one or more tracks, primary key 
            are tracks id and secondary tracks are dataTypes
        :param mode: :py:func:`str` class of the object that is going to be 
            generated
             
        :returns: d_dataTypes_merge dictionary that contains the joined tracks and
                  the new dictionary with colors assign by data type
         
        """
        d_dataTypes_merge = {}
        new_dataTypes = set()
        
        for key, nest_dict in dict_d.items():
            
            d_dataTypes_merge[key] = {}                        
            
            for key_2, data in nest_dict.items(): 
                
                if not d_dataTypes_merge[key].has_key('_'.join(nest_dict.keys())):
                    d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = data                    
                    new_dataTypes.add('_'.join(nest_dict.keys())) 
                else:                    
                    d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = d_dataTypes_merge[key]['_'.join(nest_dict.keys())] + data
                    new_dataTypes.add('_'.join(nest_dict.keys()))          
        
        #New dataTypes only set if objects is bedGraph. Bed objects needs to 
        #know all original dataTypes to display them with different colors
        if mode == 'bedGraph':
            self.dataTypes = new_dataTypes
            
        return (d_dataTypes_merge)
    
    def track_convert2bed(self, track, in_call=False, **kwargs):
        """
        Converts data belonging to a single track (in the form of a list of tuples) in
        an object of class Bed
        
        :param track: :py:func:`list` of tuples containing data of a single track
        :param False in_call: If False the call to the function is from the user otherwise
            is from inside :py:func: `convert2single_track()`
        :param None color_restrictions: Set colors not to be used #TODO this is not clear example??        
                
        :returns: Bed object
        
        """        

        #This fields are mandatory in objects of class Bed
        _bed_fields = ["track","chromStart","chromEnd","dataTypes", "dataValue"]
        
        #Check whether these fields are in the original otherwise raise exception
        try:
            [self.fields.index(f) for f in _bed_fields]
        except ValueError:
            raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))

#         if (not in_call and len(self.list_tracks) != 1):
        if (not in_call and len(self.list_tracks_filt) != 1):
            raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bed" % (self.path))
        
        i_track = self.fields.index("track")
        i_chr_start = self.fields.index("chromStart")
        i_chr_end = self.fields.index("chromEnd")
        i_data_value = self.fields.index("dataValue")
        i_data_types = self.fields.index("dataTypes")
        
        #Generate dictionary of field and color gradients
        color_restrictions = kwargs.get('color_restrictions', None)
        _dict_col_grad = assign_color (self.dataTypes, color_restrictions)
                
        step = (float(self.range_values[1]) - float(self.range_values[0])) / 9

        if step == 0: 
            _intervals = [0, self.range_values[1]] 
        else: 
            _intervals = list(arange(float(self.range_values[0]),float(self.range_values[1]), step))
        
        for row in track:
            temp_list = []
            temp_list.append("chr1")
            temp_list.append(row[i_chr_start])
            temp_list.append(row[i_chr_end])
            temp_list.append(row[i_data_types])  
            temp_list.append(row[i_data_value])   
            temp_list.append("+")
            temp_list.append(row[i_chr_start])
            temp_list.append(row[i_chr_end])
            
            for i,v in enumerate(_intervals):    
                d_type = row [self.fields.index("dataTypes")]
                global color
                color = _dict_col_grad[d_type][len(_intervals)-1]

                if float(row[i_data_value]) <= v:                    
                    color = _dict_col_grad[d_type][i-1]                                 
                    break

            temp_list.append(color)          
            
            yield(tuple(temp_list))

    def track_convert2bedGraph(self, track, in_call=False, window=300, **kwargs):
        """
        Converts a single data belonging to a single track in a list of tuples in
        an object of class BedGraph. The data is grouped in time windows.
            
        :param track: :py:func:`list` of tuples containing data of a single track
        :param False in_call: If False the call to the function is from the user otherwise
            is from inside :py:func: `convert2single_track()`
        :param window: :py:func:`int` length of windows inside bedGraph file in seconds (default 300)
                 
        :returns: BedGraph object
        """
        
        #This fields are mandatory in objects of class BedGraph
        _bed_fields = ["track","chromStart","chromEnd","dataValue"] 
        
        #Check whether these fields are in the original otherwise raise exception
        try:
            idx_f = [self.fields.index(f) for f in _bed_fields]                          
        except ValueError:
            raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))
        
#         if (not in_call and len(self.list_tracks)  != 1):            
        if (not in_call and len(self.list_tracks_filt)  != 1):
            raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bedGraph" % (self.path))
        
        i_track = self.fields.index("track")
        i_chr_start = self.fields.index("chromStart")
        i_chr_end = self.fields.index("chromEnd")
        i_data_value = self.fields.index("dataValue")
#         ini_window = 0 #ojo
        ini_window = 1
        delta_window = window      
        end_window = delta_window
        partial_value = 0 
        cross_interv_dict = {}
        
        #When the tracks have been join it is necessary to order by chr_start
        track = sorted(track, key=itemgetter(*[i_chr_start]))
                              
        for row in track:
            temp_list = []
            chr_start = row[i_chr_start]
            chr_end = row[i_chr_end]
            data_value = float(row[i_data_value])
            self.fields.index(f) 
            
            #Intervals happening after the current window
            #if there is a value accumulated it has to be dumped otherwise 0
            if chr_start > end_window:
                while (end_window < chr_start):                                      
                    partial_value = partial_value + cross_interv_dict.get(ini_window,0)
                    temp_list.append("chr1")
                    temp_list.append(ini_window)
                    temp_list.append(end_window)
                    temp_list.append(partial_value)
                    partial_value = 0
#                     ini_window += delta_window + 1 #ojo
                    ini_window += delta_window
#                     end_window += delta_window + 1 #ojo
                    end_window += delta_window                                 
                    yield(tuple(temp_list))
                    temp_list = []
    
                #Value must to be weighted between intervals
                if chr_end > end_window:                
                    value2weight = data_value
                    end_w = end_window
                    start_new = chr_start
                    end_new = chr_end
                    
                    for start_w in range (ini_window, chr_end, delta_window):
                        weighted_value = 0.0
                        
                        if (end_w == start_w):
                            weighted_value = float(end_w - start_new + 1) / float(end_new - start_new)
                        else:                                                           
                            weighted_value = float(end_w - start_new) / float(end_new - start_new)
                            #print "end_w - start_new) / (end_new - start_new)", (end_w, start_new, end_new, start_new) #del
#                             weighted_value= 9/2
                            #print "weighted value",weighted_value #del  
#                             print "value2weight..............", (chr_end, end_window, value2weight, weighted_value)
                            
                        weighted_value *= value2weight
                        cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)                      
                        start_new = end_w
                        value2weight = value2weight - weighted_value                        
    
                        if ((end_w + delta_window) >= chr_end):
                            new_start_w = start_w + delta_window
                            cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
                            break
                        
                        end_w = end_w + delta_window
                else:
                    partial_value = partial_value + data_value
                            
            elif (chr_start <= end_window and chr_start >= ini_window):
                if chr_end <= end_window:
                    partial_value = partial_value + data_value                 
                
                else:
                    value2weight = data_value
                    end_w = end_window
                    start_new = chr_start
                    end_new = chr_end
                    
                    for start_w in range (ini_window, chr_end, delta_window):
                        weighted_value = 0
                        
                        if (end_w == start_w):
                            weighted_value = float(end_w - start_new + 1) / float(end_new - start_new)
                        else:    
                            weighted_value = float(end_w - start_new) / float(end_new - start_new)
                            
                        weighted_value *= value2weight
                        cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)
                        start_new = end_w
                        value2weight = value2weight - weighted_value
                        
                        if ((end_w + delta_window) >= chr_end):
                            new_start_w = start_w + delta_window
                            cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
                            break
                        
                        end_w = end_w + delta_window    
            else:            
                print >> stderr,("FATAL ERROR: Something went wrong")

        #Last value just printed out
        temp_list.append("chr1")
        temp_list.append(ini_window)
        temp_list.append(end_window)
        temp_list.append(data_value)
        yield(tuple(temp_list))
                      
class Bed(GenomicContainer):
    """
    A :class:`~pergola.tracks.GenomicContainer` object designed to include specific 
    fields and features of **bed files**
    
    Default fields are
        ::
        
         ['chr','start','end','name','score','strand',
          'thick_start','thick_end','item_rgb']
    
    :returns: Bed object    
        
    """
    def __init__(self, data, **kwargs):
        kwargs['format'] = 'bed'
        kwargs['fields'] = ['chr','start','end','name','score','strand',
                            'thick_start','thick_end','item_rgb']
        
        GenomicContainer.__init__(self,data,**kwargs)

class BedGraph(GenomicContainer):
    """
    A :class:`~pergola.tracks.GenomicContainer` object designed to include specific 
    fields and features of **bedGraph files**
    
    .. attribute:: color
       Gradient of colors that assign by value to display in the genome browser
       
    Default fields are
        ::
        
         ['chr','start','end', 'score']
    
    :returns: BedGraph object  
          
    """
    def __init__(self, data, **kwargs):
        kwargs['format'] = 'bedGraph'
        kwargs['fields'] = ['chr','start','end','score']        
        self.color_gradient = kwargs.get('color',_blue_gradient)
        GenomicContainer.__init__(self,data,**kwargs)
    
    def win_mean (self):
        print "........................................"
        print self.data
        n_tracks = len (self.track.split("_"))

        # TODO if number of trakcs is 1 exit returning self
        self.data = self._win_mean(self.data, n_tracks)
        return (self)
    
    def _win_mean (self, data, n_tracks):     
        for row in data:
           temp_list = []
           for i, v in enumerate(row):            
                
                if i == 3:
                     temp_list.append (v/n_tracks)
                else:
                    
                    temp_list.append (v)
                
           yield (tuple(temp_list))
                
def assign_color (set_dataTypes, color_restrictions=None):
    """
    Assign colors to fields randomly. It is optional to set given color to given 
    dataTypes,  a restricted color will no be used for the remaining dataTypes.
    
    :param set_dataTypes: :py:func:`set` containing dataTypes names that should 
        be linked to color gradient
    :param color_restrictions: A :py:func:`dict` that has as key dataTypes and as  
        values colors that are set by the user          
        ::  
        
            {'dataType': 'black'}
            
        Possible color gradients are
        ::
         
             'black', 'blue', 'red', 'green' 
    
    :returns: d_dataType_color dictionary with dataTypes as keys and color gradients
        as values
    
    """
    d_dataType_color = {}
    colors_not_used = []
    
    if color_restrictions is not None:
        rest_colors = (list (color_restrictions.values()))

        #If there are restricted colors they should be on the default colors list
        if not all(colors in _dict_colors for colors in rest_colors):
            raise ValueError("Not all restricted colors are available") 
             
        #If there are fields link to related colors they also must be in the data type list 
        if not all(key in set_dataTypes for key in color_restrictions):                                  
            raise ValueError("Some values of data types provided as color restriction are not present in the file", (set_dataTypes, color_restrictions))
            
        for dataType in color_restrictions:
            d_dataType_color[dataType] = _dict_colors[color_restrictions[dataType]] 
    
        colors_not_used = _dict_colors.keys()
        colors_not_used.remove (color_restrictions[dataType])

    for dataType in set_dataTypes:        
        if not colors_not_used:
            colors_not_used = _dict_colors.keys() 
        
        if dataType in d_dataType_color:
            print ("Data type color gradient already set '%s'."%(dataType))
        else:
            d_dataType_color[dataType] = _dict_colors[colors_not_used.pop(0)]    
    
    return d_dataType_color
