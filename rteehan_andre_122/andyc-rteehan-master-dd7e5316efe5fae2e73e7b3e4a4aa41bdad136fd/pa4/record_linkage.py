# CS122: Linking restaurant records in Zagat and Fodor's list
# Ryan Teehan and Andrew Chuang


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jellyfish
import util


def find_matches(mu, lambda_, outfile='./matches.csv', block_on=None):
    
    zagat_file = './zagat.txt'
    fodor_file = './fodors.txt'
    pairs_file = './known_pairs.txt'

    #
    # ----------------- YOUR CODE HERE ------------------------
    #

    zagat = zagat_df_creator(zagat_file)
    fodor = fodor_file(fodor_file)

    matches = known_pairs_parser(pairs_file, zagat, fodor)
    unmatches = create_unmatches(zagat, fodor)
    match_scores, unmatch_scores = create_scores(matches, \
        unmatches, zagat, fodor)

    probabilities = create_vectors(matches, unmatches)

    histogram_creator(matches, unmatches)

    matches, poss_match, unmatches = determining_matches(probabilities, \
        zagat, fodor, mu, lambda_, outfile, block_on = None)

    return matches, poss_match, unmatches


def replacer(not_null, df_1, df_2):
    for i in not_null:
        if i == "True":
            index = not_null.index(i)
            df_1['restaurant'][index] = df_2[0][index]
            df_1['address'][index] = df_2[1][index] 

def zagat_df_creator(zagat_file):
    '''
    Function creates a dataframe from file containing
    restaurant names and addresses from Zagat reviews.

    Inputs:
       zagat_file (txt file): file containing names and addresses

    Outputs:
        final_zagat_df (dataframe): dataframe containing split 
        up name address attributes of restaurants. 
    '''
    zagat_df = pd.read_csv(zagat_file, header = None)
    zagat_df.columns = ['nameaddress']
    df_1 = zagat_df['nameaddress'].str.\
    extract(r'^([^\d]*)(\d.*)$', expand=True)
    df_1.columns = ['restaurant', 'address']

    df_2 = df_2 = zagat_df['nameaddress'].str.\
    extract(r'^([^\d]*)(The\s\d.*)$', expand=True)
    not_null_1 = df_2[0].notnull()
    replacer(not_null_1, df_1, df_2)
    
    df_3 = zagat_df['nameaddress'].str.\
    extract(r'^(\d*\s[^\d]*)(\d.*)$', expand=True)
    not_null_2 = df_3[0].notnull()
    replacer(not_null_2, df_1, df_3)

    df_1['restaurant'][150] = "Oyster Bar"
    df_1['address'][150] = "lower level New York City"
    
    df_1['restaurant'][176] = "Tavern on the Green"
    df_1['address'][176] = "Central Park West New York City"
    
    df_1['restaurant'][73] = "R-23"
    df_1['address'][73] = "923 E. Third St. Los Angeles"
    
    df_1['restaurant'][14] = "Cafe '50s"
    df_1['address'][14] = "838 Lincoln Blvd. Venice"

    df_1['restaurant'][149] = "One if by Land"
    df_1['address'][149] = "TIBS 17 Barrow St. New York City"    

    city_df = df_1['address'].str.extract(r'(.*)((?:Sts\.?)|(?:Aves\.?)|'\
    '(?:St\.)|(?:Rd\.?)|(?:Blvd\.?)|(?:Dr\.?)|(?:Circle\.?)|(?:Plaza)|'\
    '(?:Hwy\.?)|(?:Way)|(?:PCH)|(?:Pl\.?)|(?:Ave\.?)|(?:Walk)|'\
    '(?:Sq\.?)|(?:Ln\.?)|(?:Broadway)|(?:Pkwy\.?)|'\
    '(?:Court)|(?:fl\.))(.*)''', expand = True)

    address_df = city_df[0] + city_df[1]
    addresses = pd.concat([address_df, city_df[2]], axis=1)

    addresses[0][150] = "lower level"
    addresses[2][150] = "New York City"

    addresses[0][163] = "240 Central Park S."
    addresses[2][163] = "New York City"

    addresses[0][176] = "Central Park West"
    addresses[2][176] = "New York City"

    addresses.columns = ["street", "city"]

    final_zagat_df = pd.concat([zagat_df, df_1, addresses], axis=1)

    for i in final_zagat_df.columns:
        final_zagat_df[i] = final_zagat_df[i].str.strip()

    return final_zagat_df
    

def fodor_df_creator(fodor_file):
    '''
    Function creates a dataframe from file containing
    restaurant names and addresses from Zagat reviews.

    Inputs:
       zagat_file (txt file): file containing names and addresses


    Outputs:
        final_zagat_df (dataframe): dataframe containing split 
        up name address attributes of restaurants. 

    '''
    fodor_df = pd.read_csv(fodor_file, header = None)
    fodor_df.columns = ['nameaddress']
    df_1 = fodor_df['nameaddress'].str.extract(r'^([^\d]*)(\d.*)$', expand=True)

    second = fodor_df['nameaddress'].str.extract(r'^(\d*)(.*)(\1.*)$', expand=True)
    
    rest_names = second[0] + second[1]

    for i in range(len(second[0])):
        if second[0][i] != "":
            df_1[0][i] = rest_names[i]
            df_1[1][i] = second[2][i]

    df_1[0][111] = "C3"
    df_1[1][111] = "103 Waverly Pl.  near Washington Sq. New York"

    df_1[0][492] = "Mifune Japan Center"
    df_1[1][492] = "Kintetsu Building  1737 Post St. San Francisco"

    df_1[0][356] = "Dante's Down the Hatch"
    df_1[1][356] = "Underground Underground Mall  Underground Atlanta Atlanta"

    df_1[0][371] = "La Grotta"
    df_1[1][371] = ("at Ravinia Dunwoody Rd.  "
        "Holiday Inn/Crowne Plaza at Ravinia  Dunwoody Atlanta")

    df_1[0][372] = "Little Szechuan"
    df_1[1][371] = "C Buford Hwy.  Northwoods Plaza  Doraville Atlanta"

    df_1[0][378] = "Mi Spia"
    df_1[1][378] = ("Dunwoody Rd.  Park Place  across "
        "from Perimeter Mall  Dunwoody Atlanta")

    df_1[0][396] = "Toulouse"
    df_1[1][396] = "B Peachtree Rd. Atlanta"

    df_1[0][461] = "Garden Court"
    df_1[1][461] = "Market and New Montgomery Sts. San Francisco"

    df_1[0][462] = "Gaylord's"
    df_1[1][462] = "Ghirardelli Sq. San Francisco"

    df_1[0][464] = "Greens"
    df_1[1][464] = "Bldg. A Fort Mason San Francisco"

    df_1[0][491] = "McCormick & Kuleto's"
    df_1[1][491] = "Ghirardelli Sq. San Francisco"

    city_df = df_1[1].str.extract(r'(.*)((?:Sts\.)|(?:Aves\.?)|(?:St\.)'\
    '|(?:Promenade)|(?:Condominium)|(?:Dunwoody)|'\
    '(?:Hyatt)|(?:Rd\.?)|(?:Blvd\.\s{1}S\s{1})|'\
    '(?:Blvd\.?)|(?:Dr\.)|(?:Park\s{1}S\s{1})|(?:Sts\.?)|(?:Hwy\.?)|(?:Way)|'\
    '(?:Pl\.)|(?:Ave\.?)|(?:Road)|(?:Sq\.?)|(?:Center)|(?:Broadway)|'\
    '(?:Pkwy\.?)|(?:Circle\.?)|(?:Park\.?)'
    '|(?:Plaza)|(?:La\.)|(?:Drive))(.*)''', expand = True)

# add exceptions
    address_df = city_df[0] + city_df[1]
    addresses = pd.concat([address_df, city_df[2]], axis=1)

    addresses[0][27] = "134 N. La Cienega"
    addresses[2][27] = "Los Angeles"

    addresses[0][356] = "Underground Underground Mall"
    addresses[2][356] = "Underground Atlanta Atlanta"

    addresses[0][372] = "C Buford Hwy.  Northwoods Plaza"
    addresses[2][372] = "Doraville Atlanta"

    addresses[0][398] = "3700 W. Flamingo"
    addresses[2][398] = "Las Vegas"

    addresses[0][454] = "804 Northpoint"
    addresses[2][454] = "San Francisco"

    addresses[0][464] = "Bldg. A"
    addresses[2][464] = "Fort Mason San Francisco"

    addresses[0][513] = "Embarcadero 4"
    addresses[2][513] = "San Francisco"

    addresses[0][514] = "Redwood Alley"
    addresses[2][514] = "San Francisco"

    final_fodor = pd.concat([fodor_df, df_1, addresses], axis=1)

    final_fodor.columns = ['nameaddress', "restaurant", \
    "address", "street", "city"]
    for i in final_fodor.columns:
        final_fodor[i] = final_fodor[i].str.strip()

    return final_fodor

def known_pairs_parser(pairsfile, zagat_df, fodor_df):
    '''
    Function creates dataframe referred to as "matches"
    that contains data from training dataset containing
    known pairs of Zagat and Fodor restaurants. 

    Inputs:
        pairsfile: File containin pairs of restaurants
        that are confirmed matches between zagat and fodor
        zagat_df: Dataframe containing information from zagat datafile
        fodor_df: Dataframe containing information from fodor datafile
    '''
    
    open_file = open(pairsfile)
    pairs = open_file.read()

    pairs = pairs.split('\n')
    pairs = [x for x in pairs if not x.startswith("#")]

    for index, line in enumerate(pairs):
        if line.startswith(' '):
            pairs[index - 1] = pairs[index - 1] + line
            pairs[index] = ''

    pairs = [x for x in pairs if not x == '']
    zagat = pairs[::2]
    fodor = pairs[1::2]
    
    matches = {'zagat': zagat, 'fodor': fodor, \
    'zagat_index': [], 'fodor_index': []}
    for rest in zagat:
        index = np.where(zagat_df['nameaddress'] == rest.strip())[0]

        matches['zagat_index'].append(str(index).strip('[]'))
    for rest2 in fodor:
        index = np.where(fodor_df['nameaddress'] == rest2.strip())[0]
        matches['fodor_index'].append(str(index).strip('[]'))

    matches['zagat_index'][1] = 106
    matches['fodor_index'][46] = 347
    matches = pd.DataFrame(data = matches)
    
    return matches

    

def unmatches(zagat, fodors):
    '''
    Function that creates data

    Inputs:
        zagat: Dataframe containing data from Zagat reviews
        fodors: Dataframe containing name, address and city from Fodor data
    '''
    zagat_sample = zagat.sample(1000, replace = True, random_state = 1234)
    zagat_sample = zagat_sample.reset_index()
    zagat_sample = zagat_sample.drop('index', axis=1)

    fodors_sample = fodors.sample(1000, replace = True, random_state = 1234)
    fodors_sample = fodors_sample.reset_index()
    fodors_sample = fodors_sample.drop('index', axis=1)

    unmatches = pd.concat([zagat_sample, fodors_sample], axis=1)
    unmatches.columns = ['zagat_nameaddress', 'zagat_rest', \
    'zagat_address_city', 'zagat_address', 'zagat_city', \
    'fodor_nameaddress', 'fodor_rest', 'fodor_address_city',\
     'fodor_address', 'fodor_city']

    return unmatches

def create_scores(matches, unmatches, zagat, fodor):
    '''
    Computes the Jaro-Winkler score between matches and unmatches for 
    each category between the Zagat and Fodor dataframes.

    Inputs:
    All inputs are dataframes
        matches: Dataframe created from known_pairs_parser
        unmatches: Dataframe created from unmatches
        zagat: Dataframe containing Zagat restaurant data
        fodor: Dataframe containing Fodor restaurant data

    Outputs:
        

    '''
    match = {'name': [], 'city': [], 'address': []}
    unmatch = {'name': [], 'city': [], 'address': []}
    for column, row in matches.iterrows():
        zagat_ind = int(row['zagat_index'])
        fodor_ind = int(row['fodor_index'])

        zag_c = zagat.iloc[zagat_ind]['city']
        fod_c = fodor.iloc[fodor_ind]['city']

        zag_a = zagat.iloc[zagat_ind]['street']
        fod_a = fodor.iloc[fodor_ind]['street']

        zag_n = zagat.iloc[zagat_ind]['restaurant']
        fod_n = fodor.iloc[fodor_ind]['restaurant']

        n_score = jellyfish.jaro_winkler(zag_n, fod_n)
        c_score = jellyfish.jaro_winkler(zag_c, fod_c)
        a_score = jellyfish.jaro_winkler(zag_a, fod_a)

        match['name'].append(n_score)
        match['city'].append(c_score)
        match['address'].append(a_score)

    for column, row in unmatches.iterrows():
        n_score = jellyfish.jaro_winkler(row['zagat_rest'], row['fodor_rest'])
        c_score = jellyfish.jaro_winkler(row['zagat_city'], row['fodor_city'])
        a_score = jellyfish.jaro_winkler(row['zagat_address'], \
            row['fodor_address'])

        unmatch['name'].append(n_score)
        unmatch['city'].append(c_score)
        unmatch['address'].append(a_score)

    match_scores = pd.DataFrame(data = match)
    unmatch_scores = pd.DataFrame(data = unmatch)

    return match_scores, unmatch_scores


def histogram_creator(matches, unmatches):
    '''
    Function creates histogram 

    Inputs:
        matches: dataframe constructed matches
        unmatches: dataframe constructed unmatches

    Outputs:
        None (histogram.pdf is created by function)

    '''
    plt.figure(1)

    plt.subplot(321)
    matches['n'].plot.hist()
    plt.title('Names from Matches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')
    
    plt.subplot(322)
    unmatches['n'].plot.hist()
    plt.title('Names from Unmatches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')
    
    plt.subplot(323)
    matches['c'].plot.hist()
    plt.title('Cities from Matches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')
    
    plt.subplot(324)
    unmatches['c'].plot.hist()
    plt.title('Cities from Unmatches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')

    plt.subplot(325)
    matches['a'].plot.hist()
    plt.title('Addresses from Matches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')

    plt.subplot(326)
    unmatches['a'].plot.hist()
    plt.title('Addresses from Unmatches')
    plt.xlabel('Jaro-Winkler Score')
    plt.ylabel('Frequency')

    plt.tight_layout()

    
    plt.savefig('histograms.pdf')
    plt.close('all')


def create_vectors(match_scores, unmatch_scores):
    '''
    Function creates vectors from match and unmatch dataframes.

    Inputs:
        match_scores: 
        unmatch_scores:

    Outputs:
        probabilities: 

    '''
    match_dict = {}
    unmatch_dict = {}

    for i in range(0, 3):
        for j in range(0, 3):
            for k in range(0, 3):
                match_dict[i, j, k] = 0
                unmatch_dict[i, j, k] = 0

    for i, row in match_scores.iterrows():
        name_category = util.get_jw_category(row['name'])
        city_category = util.get_jw_category(row['city'])
        address_category = util.get_jw_category(row['address'])
        category_vector = (name_category, city_category, address_category)
        match_dict[category_vector] += 1

    for i, row in unmatch_scores.iterrows():
        name_category = util.get_jw_category(row['name'])
        city_category = util.get_jw_category(row['city'])
        address_category = util.get_jw_category(row['address'])
        category_vector = (name_category, city_category, address_category)
        match_dict[category_vector] += 1
    
    match_probs = pd.DataFrame(list(match_dict.items()), columns = ['vect',\
    'prob'])
    unmatch_probs = pd.DataFrame(list(unmatch_dict.items()), columns = ['vect',\
    'prob'])
    match_probs['prob'] = match_probs['prob'].div(50, axis = 'index')
    unmatch_probs['prob'] = unmatch_probs['prob'].div(1000, axis = 'index')

    probabilities = match_probs.merge(unmatch_probs, how='outer', on='vect')
    probabilities = probabilities.fillna(value=0)
    probabilities.columns = ['vector', 'match_prob', 'unmatch_prob']

    return probabilities



def partitioning_vectors(probabilities, mu, lambda_):
    '''
    Function that partitions the vectors based on 
    the input dataframe of vectors with their match/unmatch probabilities.

    Inputs:
        probabilities (dataframe)
        mu
        lambda_:

    Ouputs:
        possible_v, match_v, unmatch_v (lists)
        All three returned outputs are lists containing vectors
        corresponding to the category they represent. 
    '''
    possible_v = []
    match_v = []
    unmatch_v = []

    for index, row in probabilities.iterrows():
            if row['match_prob'] == 0 and row['unmatch_prob'] == 0:
                possible_v.append(row['vector'])
                probabilities = probabilities.drop(index)
    
    probabilities['ratio'] = pd.Series(probabilities['match_prob']\
        .div(probabilities['unmatch_prob']), index = probabilities.index)

    ordered_prob = probabilities.sort('ratio', ascending = False)

    mu_count = 0
    lambda_count = 0
    w1_row = 0
    w2_row = 0
    for index, row in ordered_prob.iterrows():
        if mu >= mu_count:
            mu_count += row['unmatch_prob']
            w1_row = ordered_prob.index.get_loc(index)
        else:
            break
    reverse_list = ordered_prob.sort('ratio', ascending = True)

    for index, row in reverse_list.iterrows():
        if lambda_ >= lambda_count:
            lambda_count += row['match_prob']
            w2_row = reverse_list.index.get_loc(index)
        else:
            break

    if w2_row > w1_row:
        for index, row in ordered_prob.iterrows():
            if w1_row >= ordered_prob.index.get_loc(index):
                match_vectors.append(row['vector'])
            else:
                break
        for index, row in reverse_list.iterrows():
            if w2_row >= reverse_list.index.get_loc(index):
                unmatch_vectors.append(row['vector'])

    return match_v, possible_v, unmatch_v


def determining_matches(probabilities, zagat, fodor, \
    mu, lambda_, outfile, block_on = None):
    '''
    Function determines matches between zagat and fodor data 
    frames depending on the partitions for vectors created
    by the partitioning_vectors function. 

    Inputs:
    probabilities, zagat, fodor (dataframes)
    
    mu, lambda_ (acceptable lower and upper probabilities)

    outfile (filename to save to) 

    block_on = None (optional blocking parameter)

    '''
    match_count = 0
    poss_count = 0
    unmatch_count = 0

    matches = {'zagat_name':[], 'zagat_address': [], \
    'fodor_name':[], 'fodor_addr': []}

    matches_v, poss_match_v, unmatch_v = partitioning_vectors(probabilities, \
        mu, lambda_)

 
    for zagat_index, zagat_row in zagat.iterrows():
        for fodor_index, fodor_row in fodor.iterrows():
            zagat_name = zagat.iloc[zagat_index]['restaurant']
            zagat_city = zagat.iloc[zagat_index]['city']
            zagat_address = zagat.iloc[zagat_index]['street']

            fodor_name = fodor.iloc[fodor_index]['restaurant']
            fodor_city = fodor.iloc[fodor_index]['city']
            fodor_address = fodor.iloc[fodor_index]['street']

            name_score = jellyfish.jaro_winkler(zagat_name, fodor_name)
            city_score = jellyfish.jaro_winkler(zagat_city, fodor_city)
            addr_score = jellyfish.jaro_winkler(zagat_address, \
                fodor_address)
            
            name_category = util.get_jw_category(name_score)
            address_category = util.get_jw_category(addr_score)
            city_category = util.get_jw_category(city_score)

            vector = (name_category, address_category, \
                city_category)
            if vector in matches_v:
                match_count += 1
                match_dict['zagat_name'].append(zagat_name)
                match_dict['zagat_addr'].append(zagat_address)
                match_dict['fodor_name'].append(fodor_name)
                match_dict['fodor_addr'].append(fodor_address)                    

            elif vector in poss_match_v:
                poss_count += 1
            elif vector in unmatch_v:
                unmatches += 1
    
    matches_csv = pd.DataFrame(data = match_dict)
    matches_csv.to_csv(outfile)

    return matches, poss_match, unmatches




if __name__ == '__main__':

    num_m, num_p, num_u = find_matches(0.005, 0.005, './matches.csv', 
                                       block_on=None)

    print("Found {} matches, {} possible matches, and {} " 
              "unmatches with no blocking.".format(num_m, num_p, num_u))

