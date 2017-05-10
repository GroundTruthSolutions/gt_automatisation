"""This is a set of cleaning functions for questionnaire survey data.

These functions have been designed to work with a data set that follow GT specifications and a template
for that dataset (see the gen_templates module) These functions are intended to be loaded into an interactive
Python environment such as Jupyter or Markup.

These functions were written to interact with pandas 0.18.1, numpy 1.11.1.,  matplotlib 1.5.3, and seaborn 0.7.1,
"""

__version__ = '0.1'
__author__ = 'Tomas Folke'

# Import libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def mismatch_search(data, template):
    """Compares the columns with a data frame to the index of a transposed matrix, and identifies columns
    that don't have a match
    """
    mismatches = []
    mismatch_numbers = []
    mismatch_number = 0
    for column in data.columns:
        if column not in template.index:
            mismatches.append(column)
            mismatch_numbers.append(mismatch_number)
        mismatch_number +=1
    print mismatches
    return mismatches, mismatch_numbers

def find_suggested_labels(mismatches, template):
    """Finds suggested labels for mismatched column names by comparing the prefix of the mismatched columns
    with the prefixes in the transposed template.
    """
    suggestion_list = []
    mismatch_prefixes = [mismatch.split('_')[0] for mismatch in mismatches]
    for label in template.index:
        if label.split('_')[0] in mismatch_prefixes:
            suggestion_list.append(label)
    return suggestion_list

def gen_match_dict(mismatches, suggestions):
    """Creates a dictionary from two lists, where the first list contains keys and the second contains data."""
    matching_dict ={}
    mismatches_no_partner = []
    for mismatch in mismatches:
        match = False
        for suggestion in suggestions:
                if mismatch.split('_')[0] == suggestion.split('_')[0]:
                    matching_dict[mismatch] = suggestion
                    match = True
        if match == False:
            mismatches_no_partner.append(mismatch)

    if len(mismatches) == len(matching_dict):
        return matching_dict
    else:
        return np.nan
        print 'Matching failed, the following data columns lack suggestions:'
        print mismatches_no_partner

def print_response_overview(data, columns):
    """Prints frequency counts for a list of columns in a data frame"""
    for column in columns:
        print column
        print np.sort(data.loc[:, column].unique())
        print

def count_response_proportions(data, template, columns):
    """Prints response proportions for likert scale and binary questions in a column list"""
    for column in columns:
        temp = pd.DataFrame(data.loc[:, column].value_counts(normalize=True))
        temp = temp.reset_index()
        temp.columns = column, 'frequency'
        temp = temp.sort_values(by=column).reset_index(drop=True)
        if template.loc[column, 'question_type'] == 'likert':
            print temp
        elif template.loc[column, 'question_type'] == 'binary':
            print temp

def delete_dont_knows(data, columns):
    """Deletes "don't know" and "don't want to answer responses" from specified columns"""
    data.loc[:, columns] = data.loc[:, columns].replace(['6_dont_know', '3_dont_know', '7_dont_want_to_answer', '4_dont_want_to_answer'], np.nan)

def reverse_question_scoring(data, question, include_dont_knows=False):
    """Reverses the numbers at the beginning of the response alternatives"""
    response_numbers = [np.int(answer.split('_')[0]) for answer in data[question]]
    response_numbers = np.array(response_numbers)
    if include_dont_knows == True:
        response_numbers = max(response_numbers) - response_numbers
    else:
        response_numbers = max(response_numbers) - response_numbers + 1
    response_splits = [answer.split('_') for answer in data[question]]
    updated_responses = []
    for x in range(len(response_splits)):
        updated_responses.append(np.str(response_numbers[x]) + '_' + '_'.join(response_splits[x][1:]))
    return updated_responses

def bin_quantities(data, template, quantiles=3):
    """Bins quantitative data"""
    for column in template.loc[template['question_type']=='quantity', :].index:
        print column
        extracted_quantities = []
        if data[column].dtype == str:
            for index in data.loc[data[column].notnull(), :].index:
                extracted_quantities.append(np.int(data.loc[index, column].split('_')[0]))
        extracted_quantities = data.loc[data[column].notnull(), column].values
        data.loc[data[column].notnull(), column+'_quantiles'] = pd.qcut(extracted_quantities, quantiles)

def remove_non_ascii(text):
    """Remove non-ascii symbols from a string"""
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def replace_response_categories(data, column, old_responses, new_response):
    """Quick way to reassign cell information inside a pandas dataframe."""
    data.loc[data[column].isin(old_responses), column] = new_response

def whole_number(string):
    '''Rounds a string of decimals to whole numbers'''
    return [ '%.0f' %float(elem) for elem in string.split() ]
