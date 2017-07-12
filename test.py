#!/usr/bin/env python

from __future__ import print_function

import cProfile
import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np

import swn

def stats():
    grouperLabels = ['Random',
                     'Min Dist Stars',
                     'Max Dist Stars',
                     '1/4 Min Dist Stars',
                     '1/3 Min Dist Stars',
                     '1/2 Min Dist Stars',
                     'Link Most Isolated Group',
                     'Link Smallest Group',
                     'Link Largest Group']
    # Queue for returning counts
    q = mp.Queue()
    # Create processes
    pList = list()
    for gType in xrange(9):
        p = mp.Process(target=statsgen,args=(q,gType))
        pList.append(p)
        p.start()
    # Join processes
    countsList = list()
    for gType in xrange(9):
        print('Grouper Method ' + str(gType))
        pList[gType].join()
        countsList.append(q.get())

    # Plot statistics
    font = {'size'   : 8}
    plt.rc('font', **font)
    plt.figure(figsize=(8,10))
    for gType in xrange(9):
        plt.subplot(3,3,countsList[gType][0]+1)
        plt.title(str(countsList[gType][0]) + ' - ' + grouperLabels[countsList[gType][0]],fontsize=8)
        plt.imshow(countsList[gType][1])
    plt.savefig('groupingStats.png')

def statsgen(q,gType):
    # Define statistics
    counts = np.zeros([21,16])
    numSectors = 1000
    # Generate sectors
    for i in xrange(numSectors):
        # Create generator
        gen = swn.generator.Generator()
        # Generate sector
        sec = gen.sector(gType)
        # Calculate statistics
        for s in sec.system_hex_list():
            if (s[1] % 2 == 0):
                counts[s[0]*2,  s[1]*2]   += 1.0
                counts[s[0]*2,  s[1]*2+1] += 1.0
                counts[s[0]*2+1,s[1]*2]   += 1.0
                counts[s[0]*2+1,s[1]*2+1] += 1.0
            else:
                counts[s[0]*2+1,s[1]*2]   += 1.0
                counts[s[0]*2+1,s[1]*2+1] += 1.0
                counts[s[0]*2+2,s[1]*2]   += 1.0
                counts[s[0]*2+2,s[1]*2+1] += 1.0
    q.put((gType,counts))
    

def gen(gType=1):
    # Create generator
    gen = swn.generator.Generator()
    # Set seed
    gen.set_seed('Bipiw')
    
    # Print seed
    #print(gen.seed)
    
    # Generate sector
    sec = gen.sector(gType)
    
    # Print sector map
    #sec.print_sector_map()
    
    # Print system orbit maps
    sec.print_orbit_maps()
    
    # Print sector info
    #sec.print_sector_info()
    
    # Print sector corporations
    #sec.print_corporations()
    
    # Print sector religions
    #sec.print_religions()
    
    # Create sector images
    sec.update_images()
    # Draw sector images
    sec.draw_sector()
    # Save sector images
    sec.images.save_sector_map('test/testmap.png')
    sec.images.save_sector_info('test/testinfo.png')
    sec.images.save_sector_orbits('test/map.png')

if __name__ == '__main__':
    gen()
    #stats()
    #runStats = cProfile.run('gen()', sort='cumtime')