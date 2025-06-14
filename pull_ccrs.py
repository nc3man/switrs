#!/user/bin/env python3 -tt

# Imports

import os

# Helper functions ---------------------------------------------------------
def get_CCRS_processed(root_dir, include, exclude=[]):
    # if either include=[] or exclude=[], that filter is ignored
    file_list = []
    
    for root, directories, filenames in os.walk(root_dir):
        for filename in filenames: 
            if filename[0:4]=='CCRS' and filename[-4:]=='.csv':
                if any(elem in filename for elem in include):
                   if any(elem in filename for elem in exclude)==False:
                        file_list.append(os.path.join(root, filename))              
                
    return file_list            
