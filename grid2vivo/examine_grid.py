#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    examine_grid.py: Simple VIVO

    Read the Grid data, tabulate various keys.  Display first and last entries as examples
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.1"


def main():

    import json

    grid_file = open('../grid/grid.json')
    grid_all = json.load(grid_file)

    version = grid_all['version']
    print 'Grid', version

    grid = grid_all['institutes']
    print len(grid), "institutes"

    institute = grid[0]
    print "First institute in the data"
    print json.dumps(institute, indent=4)

    print "Last institute", json.dumps(grid[-1], indent=4)

    # Determine key frequency -- how many times is each high level key used?

    counts = {}
    for institute in grid:
        for key in institute.keys():
            if key not in counts:
                counts[key] = 1
            else:
                counts[key] += 1
    print "\nFrequency of keys in Grid data for ", len(grid), "institutes\nKey\tCount"
    for key, count in counts.items():
        print key, '\t', count

    # Frequency table of status

    counts = {}
    for institute in grid:
        if institute['status'] not in counts:
            counts[institute['status']] = 1
        else:
            counts[institute['status']] += 1

    print "\nFrequency of statuses in Grid data for ", len(grid), "institutes\nStatus\tCount"
    for status, count in counts.items():
        print status, '\t', count

    # Frequency table of types

    counts = {}
    for institute in grid:
        for type in institute.get('types', []):
            if type not in counts:
                counts[type] = 1
            else:
                counts[type] += 1
    print "Frequency of types in Grid data for ", len(grid), "institutes\nType\tCount"
    for type, count in counts.items():
        print type, '\t', count

    # Frequency table of relationships

    counts = {}
    for institute in grid:
        for relationship in institute.get('relationships', []):
            if 'type' in relationship:
                type = relationship['type']
                if type not in counts:
                    counts[type] = 1
                else:
                    counts[type] += 1
    print "Frequency of types of relationships in Grid data for ", len(grid), "institutes\nType\tCount"
    for type, count in counts.items():
        print type, '\t', count

    return


if __name__ == "__main__":
    main()

