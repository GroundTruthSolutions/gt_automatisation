"""This is a set of functions to create summary tables and plots for
descriptive analyses of questionnaire data.

These functions have been designed to work with a data_cleaning.py to quickly
prepare summary information from datasets that follow GT specifications and has
an appropriate template for that dataset (see the gen_templates module). These
functions are intended to be loaded into an interactive python environment such
as Jupyter or Markup.

These functions were written to interact with pandas 0.18.1, numpy 1.11.1.,
matplotlib 1.5.3, and seaborn 0.7.1
"""

__version__ = '0.1'
__author__ = 'Tomas Folke'

# Import libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

def draw_basic_plot(table, likert=True, folder_path='../../output/'):
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
    plt.savefig(folder_path+question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig(folder_path+question_name+'.jpg', dpi=600, transparent=True)
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

def draw_disag_plot(table, likert=True, reindex_order=np.nan, folder_path='../../output/'):
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
    plt.savefig(folder_path + table2.index.name + '_breakdowns/' + question_name+'.pdf', dpi=600, transparent=True)
    plt.savefig(folder_path + table2.index.name + '_breakdowns/' + question_name+'.jpg', dpi=600, transparent=True)
    plt.close()

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

def calculate_fp_se(data= data, questions = [], N= int):
    '''Function to calculate standard errors for finite populations. Should be used instead
    instead of normal standard errors when the sample covers more than 15% of the intended
    target population'''
    std = data.loc[:, questions].std()
    n = np.float(data.loc[:, questions[0]].count())
    se = std/np.sqrt(n)
    fp_se = se*np.sqrt(((N-n)/(N-1.0)))
    fp_se = fp_se.round(2)
    return fp_se

def draw_basic_poster_plot(table, likert=True):
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
        binay_keys = [np.int(label.split('_')[0]) for label in table2.columns]
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

def draw_mean_breakdown_plot(data, breakdown, variable, filename=None):
    """Plots means as a pointplot a function of a breakdown variable"""
    if filename==None:
        filename=variable.split('_')[0]
    sns.set(style='whitegrid', font_scale=1.5)
    fig, ax = plt.subplots(figsize=(7.5, 3))
    sns.pointplot(x=breakdown, y=variable, data=data,
                  join=False, scale=1.2, errwidth=8, color='#65889d')
    plt.setp(ax.lines, zorder=100)
    plt.setp(ax.collections, zorder=100)
    ax.set(ylabel='', ylim=(1, 5), xlabel='', yticklabels=('1', '', '2', '', '3', '', '4', '', '5'))
    plt.hlines(mean_data_full[variable].mean(), -1, 3, lw=3, linestyles='dashed',
              zorder=1)

    plt.savefig('../../output/' + filename + '.pdf', dpi=600, transparent=True)
    plt.savefig('../../output/' + filename + '.png', dpi=600, transparent=True)

def draw_np_hist_plot(data=data,
            question='',
            filename='temp'):
    sns.set(style='white', font_scale=0.8)
    """ Draws a histogram of response distributions for 11-point likert
    scale questions, with colours signaling the contribution of various
    response categories to the net promoter score. Useful as a visual
    explanation of how the raw scores relate to the NPS scores"""

    data = data.loc[data[question].notnull(), question]

    # Now let's make a frequency table to plot
    frequencies = data.value_counts(sort=False)
    for number in np.arange(0, 11):
        if number not in frequencies.index:
            frequencies.set_value(number, 0)
    frequencies = frequencies.sort_index()
    max_freq = frequencies.max()

    fig, ax = plt.subplots(figsize=(mm2inch(85.55), mm2inch(45)))
    plt.bar(frequencies.index, frequencies.values, width=1)
    sns.despine(left=True)

    ax.set(yticks=[], xticks=frequencies.index+.5,
           xlabel='', xticklabels=np.arange(11), xlim=(0, 11.05),
          ylim=(0, 25))

    [ax.patches[i].set(fc='#f19891', ec='#222222', lw=0.5) for i in np.arange(7)]
    [ax.patches[i].set(fc='#ffdd86', ec='#222222', lw=0.5) for i in np.arange(7, 9)]
    [ax.patches[i].set(fc='#4aa168', ec='#222222', lw=0.5) for i in np.arange(9, 11)]

    ax.tick_params(direction='out', pad=2)
    [label.set_weight('bold') for label in ax.xaxis.get_ticklabels()]



    for rect in ax.patches:
        height = rect.get_height()
        if height != 0:
            ax.text(rect.get_x() + rect.get_width()/2, height, int(height),
                    ha='center', va='bottom', size=8, color='#666666')

    fig.subplots_adjust(top = 0.86, bottom = 0.08, right = 0.99, left = 0.01,
                hspace = 0, wspace = 0)

    savepath='../../output/' + filename

    plt.savefig(savepath+'.png', dpi=600, transparent=True)
    plt.savefig(savepath+'.pdf', dpi=600, transparent=True)
