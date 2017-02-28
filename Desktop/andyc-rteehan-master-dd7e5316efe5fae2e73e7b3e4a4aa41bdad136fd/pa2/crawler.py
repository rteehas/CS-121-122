# CS122: Course Search Engine Part 1
#
# Andrew Chuang and Ryan Teehan
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are', 'as',  'at',  'be',
                    'but',  'by',  'course',  'for',  'from',  'how', 'i',
                    'ii',  'iii',  'in',  'include',  'is',  'not',  'of',
                    'on',  'or',  's',  'sequence',  'so',  'social',  'students',
                    'such',  'that',  'the',  'their',  'this',  'through',  'to',
                    'topics',  'units', 'we', 'were', 'which', 'will', 'with', 'yet'])


### YOUR FUNCTIONS HERE

# Auxiliary functions for mini-crawler

def find_tag_list(url, soup_object, request_obj, limiting_d):
    '''
    Function finds the list of hyperlink tags from given URL and collects
    the list of URLs. 

    Inputs:
        url (string): URL to find list of further URLs from
        soup_object (soup object): Soup object obtained from using 
        Beautiful Soup on given URL
        request_obj (request object): Request object obtained from the functions 
        given in PA to obtain request object from URL 
        limiting_d (string): Limiting domain for the URLs

    Outputs:
        url_list (list): List containing all URLs that are able
        to be followed from the given URL. 

    '''
    https_url = util.get_request_url(request_obj)
    ahref_tag_list = soup_object.find_all('a', href = True)

    url_list = []

    for tag in ahref_tag_list:
        this_url = tag['href']
        newest_url = util.convert_if_relative_url(https_url, this_url)
        if util.is_url_ok_to_follow(newest_url, limiting_d):
            url_list.append(newest_url)
    
    return url_list


def add_to_queue(url_list, url_queue, unique):
    '''
    Function checks url from url_list and determines
    whether url has already been visited before. If the URL
    is unique 

    Inputs:
        url_list (list): List of URLs to check uniqueness
        url_queue (queue): Queue to put URLs into
        unique (list): List to keep track of URLs already visited

    Outputs:
        None (alters provided url_queue)
    '''

    for url in url_list:
        if url in unique:
            continue
        else:
            unique.append(url)
            url_queue.put(url)

#Function for mini-indexer

def create_index(soup_object, course_dictionary, index):
    '''
    Function maps words in description to the course indentifiers
    into the given index.

    Inputs:
        soup_object (beautiful soup object) 
        course_dictionary (dictionary)
        index (dictionary)

    Outputs:
        Alters provided index. 

    '''
    main_list = soup_object.find_all('div', class_ = "courseblock main")
    for main in main_list:
        total_text = str()
        # selects all the relevant text
        total_text += main.find('p', class_ = 'courseblocktitle').text + \
        main.find('p', class_ = 'courseblockdesc').text
        # gets rid of non-breaking spaces
        total_text = total_text.replace('\xa0', ' ')
        #finds the course identifier
        identifier = total_text[:10]
        pattern = r'[a-zA-Z][a-zA-Z0-9]+'
        word_list = re.findall(pattern, total_text)

        # selects the case where there is no subsequence
        if util.find_sequence(main) == []:
            for word in word_list:
                word = word.lower()
                if word not in INDEX_IGNORE:
                    if word not in index:
                        index[word] = set()
                        index[word].add(course_dictionary[identifier])
                    else: 
                        index[word].add(course_dictionary[identifier])
        else:
            id_list = []
            # indexes the words specific to each course in the subsequence
            for sub in util.find_sequence(main):
                all_text = str()
                all_text += sub.find('p', class_ = 'courseblocktitle').text \
                + sub.find('p', class_ = 'courseblockdesc').text
                all_text = all_text.replace('\xa0', ' ')
                identifier = all_text[:10]
                sub_words =  re.findall(pattern, all_text)
                for word in sub_words:
                    word = word.lower()
                    if word not in INDEX_IGNORE:
                        if word not in index:
                            index[word] = set()
                            index[word].add(course_dictionary[identifier])
                        else: 
                            index[word].add(course_dictionary[identifier])
                id_list.append(course_dictionary[identifier])
            # indexes words common to the subsequence
            for word in word_list:
                word = word.lower()
                if word not in INDEX_IGNORE:
                    if word not in index:
                        index[word] = set(id_list)
                    if word in index:
                        index[word].update(set(id_list))


def create_csv(index, index_filename):
    '''
    Function takes index and makes it into a csv file.

    Inputs:
        index (dictionary): Index containing mapping from code name 
        to course name. 
        index_filename (string): String that is used to be the
        name of the output file name. 

    Outputs:
       Creates csv file using the given index. CSV file is
       titled using given filename. 

    '''
    with open(index_filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in sorted(index.items()):
            for x in value:
                writer.writerow([str(x) + "|" + str(key)])


def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs: 
        CSV file of the index.
    '''

    starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/index.html"
    limiting_domain = "classes.cs.uchicago.edu"
    index = {}
    unique_list = [starting_url]
    url_queue = queue.Queue()
    url_queue.put(starting_url)
    counter = 0
    with open(course_map_filename) as data:
        course_dict = json.load(data)

    while counter < num_pages_to_crawl and not url_queue.empty():
        next_url = url_queue.get()
        request_obj = util.get_request(next_url)
        url_text = util.read_request(request_obj)
        soup = bs4.BeautifulSoup(url_text, "html5lib")
        next_tag_list = find_tag_list(next_url, soup, \
            request_obj, limiting_domain)
        create_index(soup, course_dict, index)
        add_to_queue(next_tag_list, url_queue, unique_list)
        counter += 1

    create_csv(index, index_filename)

    

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 200
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)    
        sys.exit(0)


    go(num_pages_to_crawl, course_map_filename, index_filename)




