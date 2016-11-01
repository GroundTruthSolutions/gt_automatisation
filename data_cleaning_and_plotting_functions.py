"""This is a set of cleaning and plotting functions to speed up descriptive analyses.

These functions have been designed to work with a data set that follow GT specifications and a template
for that dataset (see the gen_templates module) These functions are intended to be loaded into an interactive
python environment such as Jupyter or Markup.

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
        return np.nan()
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
        for index in data.index:
            extracted_quantities.append(np.int(data.loc[index, column].split('_')[0]))
        data[column+'_quantiles'] = pd.qcut(extracted_quantities, quantiles)

def gen_summary_table(data, question):
    """Generates summary tables for a question, including frequencies percentages and cumulative frequencies"""
    table = data[question].value_counts()
    table = pd.DataFrame(table)
    table = table.reset_index()
    table.columns = [question, 'frequency']
    if question.split('_')[0] != 'quantiles':
        table = table.sort_values(by=question, ascending=True)
    table = table.reset_index(drop=True)
    table['percent'] = table['frequency']
    table['cum_frequency'] = table['frequency']
    for index in table.index:
        if index > 0:
            table.loc[index, 'cum_frequency'] = table.loc[index, 'frequency'] + table.loc[index-1, 'cum_frequency']
    table['percent'] = table['percent']/table.loc[table.shape[0]-1, 'cum_frequency']
    table['percent'] = np.round(table['percent']*100)
    table['cum_proportion'] = table['cum_frequency']/table.loc[table.shape[0]-1, 'cum_frequency']
    return table

def draw_basic_plot(table, likert=True):
    """Generates and saves standard GT bar plots from summary tables of likert questions and binary questions."""
    sns.set(style='white')
    likert=True
    table2 = table.set_index(column)
    table2 = table2.transpose()
    table2.loc['', :] = np.zeros(len(table2.columns))

    if likert == True:
        likert_dict ={1: "#f19891", 2: "#f8cac3", 3:"#e9ecf0", 4:"#b2cfb3", 5:"#4aa168", 6:"#c9d5dd", 7:'#9bb2bf'}
        likert_keys = [np.int(label.split('_')[0]) for label in table2.columns]
        likert_colours = sns.color_palette([likert_dict[x] for x in likert_keys])
        colours = likert_colours
    else:
        binary_dict = {1: "#f19891", 2: "#4aa168", 3: "#c9d5dd", 4: '#9bb2bf'}
        binary_keys = [np.int(label.split('_')[0]) for label in table2.columns]
        binary_colours = sns.color_palette([binary_dict[x] for x in binary_keys])
        colours = binary_colours

    fig, ax = plt.subplots(figsize=(15, 2))
    table2.loc[('', 'percent'), :].plot(kind='barh', stacked=True, color=likert_colours, legend=False, width=0.6,
                                          ax=ax)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, output2.loc['percent', :].sum()), ylim=(0.7, 1.3), yticklabels=(), xticklabels=[])

     #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]
     # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 40), textcoords='offset points',
                    weight='bold', size=30, ha='center')
    question_name = table2.columns.name
    plt.tight_layout()
    plt.savefig('output/'+question_name+'.pdf', dpi=600)
    plt.savefig('output/'+question_name+'.jpg', dpi=600)
    plt.close()

def gen_disag_table(data, question, breakdown):
    """Generates summary tables for disaggregated data"""
    table = data.groupby(breakdown)[question].value_counts()
    table = pd.DataFrame(table)
    table.columns = ['frequency']
    table = table.reset_index()
    table = table.sort_values(by=[breakdown, question])
    table.reset_index(inplace=True, drop=True)
    table
    table['percent'] = table['frequency']
    table['cum_frequency'] = table['frequency']
    table['cum_proportion'] = np.nan

    for category in table[breakdown].unique():
        counter = 0
        for index in table.loc[table[breakdown]==category].index:
            if counter > 0:
                table.loc[index, 'cum_frequency'] = table.loc[index, 'frequency'] + table.loc[index-1, 'cum_frequency']
            counter +=1
        table.loc[table[breakdown]==category, 'percent'] = (table.loc[table[breakdown]==category, 'percent']/
        table.loc[table.loc[table[breakdown]==category, :].index.max(), 'cum_frequency'])
        table.loc[table[breakdown]==category, 'percent'] = table.loc[table[breakdown]==category, 'percent']*100
        table.loc[table[breakdown]==category, 'cum_proportion'] = (table.loc[table[breakdown]==category, 'cum_frequency']/
        table.loc[table.loc[table[breakdown]==category, :].index.max(), 'cum_frequency'])
    return table

def draw_disag_plot(table, likert=True, reindex_order=np.nan):
    """Generates and saves standard GT bar plots from disaggregated tables"""

    # this formula ensures that the figure gets 2 inches wider for each category, with an additional inch for
    # the whitespaces between categories
    fig_height = len(table.loc[:, table.columns[0]].unique())*2
    fig, ax = plt.subplots(figsize=(15, fig_height))

    # preparing and plotting the basic graph
    table2 = table.pivot(index=table.columns[0], columns=table.columns[1], values='percent')
    if reindex_order == reindex_order:
        table2 = table2.reindex(reindex_order)
    index = list(table2.index)
    if likert == True:
        likert_dict ={1: "#f19891", 2: "#f8cac3", 3:"#e9ecf0", 4:"#b2cfb3", 5:"#4aa168", 6:"#d1b26f", 7:'#ad8150'}
        likert_keys = [np.int(label.split('_')[0]) for label in table2.columns]
        likert_colours = sns.color_palette([likert_dict[x] for x in likert_keys])
        colours = likert_colours
    else:
        binary_dict = {1: "#f19891", 2: "#4aa168", 3: "#d1b26f", 4: '#ad8150'}
        binary_keys = [np.int(label.split('_')[0]) for label in table2.columns]
        binary_colours = sns.color_palette([binary_dict[x] for x in binary_keys])
        colours = binary_colours

    index.reverse()
    table2 = table2.reindex(index)
    table2.plot(kind='barh', stacked=True, color=colours, ax=ax, legend=False, width=0.6)

    # remove black lines around the figure
    sns.despine(top=True, right=True, left=True, bottom=True)
    alternatives = ax.get_yticklabels()
    alternatives = [alternative.get_text() for alternative in list(alternatives)]
    alternatives.reverse()
    ax.set(xticklabels=[], ylabel='', yticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 30), textcoords='offset points',
                   weight='bold', size=30, ha='center')
    # savefig
    question_name = table2.columns.name.split('_')[0] + '_by_' + table2.index.name.split('_')[0] + '_order'
    for alternative in alternatives:
        question_name = question_name + '_' + np.str(alternative)
    plt.tight_layout()
    fig.gca().set_axis_off()
    fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
    hspace = 0, wspace = 0)
    ax.margins(0,0)
    fig.gca().xaxis.set_major_locator(plt.NullLocator())
    fig.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(r'output/' + table2.index.name + '_breakdowns/' + question_name+'.pdf', dpi=600, bbox_inches='tight', pad_inches=0)
    plt.savefig(r'output/' + table2.index.name + '_breakdowns/' + question_name+'.jpg', dpi=600, bbox_inches='tight', pad_inches=0)
    plt.close()


def remove_non_ascii(text):
    """Remove non-ascii symbols from a string"""
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def gen_long_table(data, question_lists_1, filename):
    long_list_1 = data.loc[:, question_lists_1].copy()
    long_list_1 = pd.melt(long_list_1, value_vars=list(question_lists_1))
    freq_count = pd.DataFrame(long_list_1['value'].value_counts())
    percent_count = pd.DataFrame(long_list_1['value'].value_counts(normalize=True))
    freq_count['percent'] = percent_count['value']
    freq_count['percent'] = freq_count['percent']*100
    clean_index=[]
    for text in freq_count.index:
        clean_index.append(remove_non_ascii(text))
    freq_count.index = clean_index
    freq_count.columns = ['frequency', 'percent']
    freq_count.to_csv(filename)

def replace_response_categories(data, column, old_responses, new_response):
    """Quick way to reassign cell information inside a pandas dataframe."""
    data.loc[data[column].isin(old_responses), column] = new_response
