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

def gen_summary_table(data, question):
    """Generates summary tables for a question, including frequencies percentages and cumulative frequencies"""
    table = data[question].value_counts(sort=False)
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
    table2 = table.set_index(table.columns[0])
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

    fig, ax = plt.subplots(figsize=(7.5, 1))
    table2.loc[('', 'percent'), :].plot(kind='barh', stacked=True, color=colours, legend=False, width=0.6,
                                              ax=ax)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, table2.loc['percent', :].sum()), ylim=(0.7, 1.3), yticklabels=(), xticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 29), textcoords='offset points',
                    weight='bold', size=15, ha='center')
    question_name = table2.columns.name
    fig.subplots_adjust(top = 0.99, bottom = 0.01, right = 0.99, left = 0.01,
            hspace = 0, wspace = 0)
    plt.savefig('output/'+question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig('output/'+question_name+'.jpg', dpi=600, transparent=True)
    plt.close()

def draw_basic_poster_plot(table, likert=True):
    """Generates and saves standard GT bar plots from summary tables of likert questions and binary questions.
    The dimensions of the generated plots are adapted to suit a poster format. """
    sns.set(style='white')
    table2 = table.set_index(table.columns[0])
    table2 = table2.transpose()
    table2.loc['', :] = np.zeros(len(table2.columns))

    if likert == True:
        likert_dict ={1: "#f19891", 2: "#f8cac3", 3:"#e9ecf0", 4:"#b2cfb3", 5:"#4aa168", 6:"#c9d5dd", 7:'#9bb2bf'}
        likert_keys = table2.columns
        likert_colours = sns.color_palette([likert_dict[x] for x in likert_keys])
        colours = likert_colours
    else:
        binary_dict = {1: "#f19891", 2: "#4aa168", 3: "#c9d5dd", 4: '#9bb2bf'}
        binary_keys = table2.columns
        binary_colours = sns.color_palette([binary_dict[x] for x in binary_keys])
        colours = binary_colours

    fig, ax = plt.subplots(figsize=(mm2inch(220), mm2inch(23.5)))
    table2.loc[('', 'percent'), :].plot(kind='barh', stacked=True, color=colours, legend=False, width=0.6,
                                              ax=ax)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, table2.loc['percent', :].sum()), ylim=(0.7, 1.3), yticklabels=(), xticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=1) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 23), textcoords='offset points',
                    weight='bold', size=30, ha='center')
    question_name = table2.columns.name
    fig.subplots_adjust(top = 0.99, bottom = 0.01, right = 1, left = 0,
            hspace = 0, wspace = 0)
    plt.savefig('../../output/'+question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig('../../output/'+question_name+'.jpg', dpi=600, transparent=True)
    plt.close()

def gen_disag_table(data, question, breakdown):
    """Generates summary tables for disaggregated data"""
    table = data.groupby(breakdown)[question].value_counts(sort=False)
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
    sns.set(style='white')
    fig_height = len(table.loc[:, table.columns[0]].unique())
    fig, ax = plt.subplots(figsize=(7.5, fig_height))

    # preparing and plotting the basic graph
    table2 = table.pivot(index=table.columns[0], columns=table.columns[1], values='percent')
    if reindex_order == reindex_order:
        table2 = table2.reindex(reindex_order)
    index = list(table2.index)
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

    index.reverse()
    table2 = table2.reindex(index)
    table2.plot(kind='barh', stacked=True, color=colours, ax=ax, legend=False, width=0.6)

    # remove black lines around the figure
    sns.despine(top=True, right=True, left=True, bottom=True)
    alternatives = ax.get_yticklabels()
    alternatives = [alternative.get_text() for alternative in list(alternatives)]
    alternatives.reverse()
    ax.set(xlim=(0, 100), ylabel='', yticklabels=[], xticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 15), textcoords='offset points',
                   weight='bold', size=15, ha='center')
    # savefig
    question_name = table2.columns.name.split('_')[0] + '_by_' + table2.index.name.split('_')[0] + '_order'
    for alternative in alternatives:
        question_name = question_name + '_' + np.str(alternative).split('_')[0]

    fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
    hspace = 0, wspace = 0)
    plt.savefig(r'output/' + table2.index.name + '_breakdowns/' + question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig(r'output/' + table2.index.name + '_breakdowns/' + question_name+'.jpg', dpi=600, transparent=True)
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

def draw_time_series_plot(data, question, session, mean, filename):
    """Draw plot to track mean changes across rounds"""
    question_data = data.loc[(data['Question']==question), :].copy()

    sns.set(font_scale=0.8, style='whitegrid')
    fig, ax = plt.subplots(figsize=(3.22, 1.23))

    sns.pointplot(data=question_data,
                 x=session, y=mean, markers='D', color='#65889d', scale=0.5)
    ax.set(ylabel='', ylim=(1, 5), xlabel='',
            xticklabels= '',#['Round %d' %round for round in example.loc[:, 'Round']],
            yticklabels=('1','', '2', '', '3', '', '4', '', '5'))

    [ax.text(p[0], p[1]+0.3, p[1], color='black', ha='center', size=9) for p in zip(ax.get_xticks(),
            question_data.loc[:, 'Mean'].round(1))]

    fig.subplots_adjust(top = 0.96, bottom = 0.04, right = 0.99, left = 0.06,
            hspace = 0, wspace = 0)
    plt.savefig(filename + '.pdf', dpi=600, transparent=True)
    plt.savefig(filename + '.png', dpi=600, transparent=True)
    plt.close()

def draw_basic_exp_plot(table, likert=True):
    """Generates and saves standard GT bar plots from summary tables of likert questions and binary questions.
    Gives a title to make the questions easy to identify, not meant for report writing."""
    sns.set(style='white')
    table2 = table.set_index(table.columns[0])
    table2 = table2.transpose()
    table2.loc[' ', :] = np.zeros(len(table2.columns))
    question_name = ' '.join(table2.columns.name.split('_'))

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

    fig, ax = plt.subplots(figsize=(7.5, 1))
    table2.loc[('', 'percent'), :].plot(kind='barh', stacked=True, color=colours, legend=False, width=0.6,
                                              ax=ax, title=question_name)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, table2.loc['percent', :].sum()), ylim=(0.7, 1.3), yticklabels=(), xticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 11), textcoords='offset points',
                    weight='bold', size=15, ha='center')
    plt.tight_layout()

def draw_disag_exp_plot(table, likert=True, reindex_order=np.nan):
    """Generates and saves standard GT bar plots from disaggregated tables. Contains Question titles and
    category labels. For exploratory use, not report writing."""

    # this formula ensures that the figure gets 2 inches wider for each category, with an additional inch for
    # the whitespaces between categories
    fig_height = len(table.loc[:, table.columns[0]].unique())
    fig, ax = plt.subplots(figsize=(7.5, fig_height))

    # preparing and plotting the basic graph
    table2 = table.pivot(index=table.columns[0], columns=table.columns[1], values='percent')
    if reindex_order == reindex_order:
        table2 = table2.reindex(reindex_order)
    index = list(table2.index)
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

    index.reverse()
    table2 = table2.reindex(index)
    question_name = ' '.join(table2.columns.name.split('_'))
    table2.plot(kind='barh', stacked=True, color=colours, ax=ax, legend=False, width=0.6,
               title=question_name)

    # remove black lines around the figure
    sns.despine(top=True, right=True, left=True, bottom=True)
    alternatives = ax.get_yticklabels()
    alternatives = [alternative.get_text() for alternative in list(alternatives)]
    alternatives.reverse()
    ax.set(xticklabels=[], ylabel='')

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 15), textcoords='offset points',
                   weight='bold', size=15, ha='center')
    plt.tight_layout()

def whole_number(string):
    '''Rounds a string of decimals to whole numbers'''
     return [ '%.0f' %float(elem) for elem in string.split() ]

def write_large_freq_table(data, column_list, name):
    "Combines data from several columns of open responses into one large frequency table"
    long_list = pd.melt(data, value_vars=column_list)
    frequency_table = pd.DataFrame(long_list['value'].value_counts())
    frequency_table.to_excel(writer, name, startrow=0)

def gen_multiple_choice_tables(option_list, question):
    """This is a function that generates frequency and output tables for multiple choice questions.
    It takes two inputs: A list of column names for the various options, and the column name of the
    question the tables should be generated for."""
    table_list = []

    for option in option_list:
        table = data.groupby(option)[question].value_counts(sort=False)
        table = pd.DataFrame(table)
        table.columns = ['frequency']
        table = table.reset_index()
        table = table.loc[table[table.columns[0]]==True, :]
        table.loc[:, table.columns[0]] = table.columns[0]
        table.columns = ['service', question, 'frequency']
        table['percent'] = table['frequency']/np.float(table['frequency'].sum()) * 100
        table['percent'] = table['percent'].round()
        table_list.append(table)

    long_table = pd.concat(table_list)
    long_table.sort_values(by=['service', question])
    long_table['service'] = long_table['service'].map(lambda x: x[3:])

    freq_table = long_table.pivot(index='service', columns=question, values='frequency')
    freq_table = freq_table.fillna(0)

    per_table = long_table.pivot(index='service', columns=question, values='percent')
    per_table = per_table.fillna(0)
    return long_table, freq_table, per_table

def draw_np_plot(data, question):
    '''Draw plots for net promoter distributions, adhearing to the
    Keystone standard.'''
    sns.set(style='white')

    # generating table
    table = pd.DataFrame(data[question].value_counts(sort=False, normalize=True))
    table[question] = table[question]*100
    table = table.round()
    table = table.transpose()

    #specifying the colours
    colour_dict = {'detractor': "#f19891", 'passive': "#ffdd86", 'promoter':"#4aa168"}
    colour_keys = table.columns
    colours = sns.color_palette([colour_dict[x] for x in colour_keys])

    # drawing the plot
    fig, ax = plt.subplots(figsize=(mm2inch(171.097), mm2inch(10.231)))
    table.plot(kind='barh', stacked=True, legend=False, width=1,
                            color=colours, ax=ax)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, table.sum(1).values[0]), yticklabels=[], xticklabels=[])

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 4), textcoords='offset points',
                    weight='bold', size=15, ha='center')

    fig.subplots_adjust(top = 0.99, bottom = 0.01, right = 0.99, left = 0.01,
            hspace = 0, wspace = 0)

    # saving the figure
    question_name = ('_').join(question.split('. '))
    plt.savefig('../../output/'+question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig('../../output/'+question_name+'.jpg', dpi=600, transparent=True)
    plt.close()

def draw_exp_np_plot(data, question):
    '''A version of the netpromoter plot for exploratory pdfs.'''
    sns.set(style='white')

    # generating table
    table = pd.DataFrame(data[question].value_counts(sort=False, normalize=True))
    table[question] = table[question]*100
    table = table.round()
    table = table.transpose()

    #specifying the colours
    colour_dict = {'detractor': "#f19891", 'passive': "#ffdd86", 'promoter':"#4aa168"}
    colour_keys = table.columns
    colours = sns.color_palette([colour_dict[x] for x in colour_keys])

    # drawing the plot
    fig, ax = plt.subplots(figsize=(mm2inch(171.097), mm2inch(10.231)))
    table.plot(kind='barh', stacked=True, legend=False, width=1,
                            color=colours, ax=ax)
    sns.despine(top=True, right=True, left=True, bottom=True)
    ax.set(xlim=(0, table.sum(1).values[0]), xticklabels=[],
    yticklabels=[], title=question)

    #create the white spaces between the squares
    rects = ax.patches
    [rect.set(edgecolor='white', linewidth=3) for rect in rects]

    # Adding the percentage labels
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate("{0:.0f}".format(p.get_width()),
                    (p.get_x() + p.get_width()/2, p.get_y()), xytext=(0, 4), textcoords='offset points',
                    weight='bold', size=15, ha='center')

    fig.subplots_adjust(top = 0.99, bottom = 0.01, right = 0.99, left = 0.01,
            hspace = 0, wspace = 0)
