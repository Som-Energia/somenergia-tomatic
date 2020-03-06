#!/usr/bin/env python

import sys

def main():
    '''TODO: sanitize'''
    first_dict_yaml = sys.argv[1]
    second_dict_yaml = sys.argv[2]

    from yamlns import namespace as ns

    first_dict = ns.load(first_dict_yaml)
    second_dict = ns.load(second_dict_yaml)

    merged_dict = first_dict
    for k2,v2 in second_dict.items():
        v1 = first_dict.get(k2,0)
        merged_dict[k2] = v1 + v2
        #print('{}: {} + {} = {}'.format(k2,v1,v2,merged_dict[k2]))

    print(merged_dict.dump())

    return merged_dict

if __name__ == "__main__":
	main()
