"""gen_examples generates simulated data and a response sheet from a template file.

This module is intended to run from the terminal. First the user inputs the path and filename
to a template csv-file (generated by gen_templates.py). And then they enter additional information
to generate the simulated data, if necessary (e.g. giving a mean and a standard deviation to the
distribution of responses for a quantititative variable. Finally the user gives paths and filenames
for where they want to save the simulated data and the response sheet.

This module was written to interact with pandas 0.18.1, numpy 1.11.1. and itertools 9.7.0-
"""

__version__ = '0.1'
__author__ = 'Tomas Folke'

# import libraries
import numpy as np
import pandas as pd
#import itertools as it

def load_template():
    """Loads csv from a path specificed by the user and returns a pandas data frame"""
    csv_path =  raw_input("Please specify path to template")
    template = pd.read_csv(csv_path, header=0, index_col=0)
    return template

def extract_response_options(template, column):
    """Transforms the response options inside a data frame cell from a string to a list"""
    options = template.loc['response_options', column].translate(None, "[]',")
    options = options.split()
    return options

def extract_multiple_choice_combinations(options):
    """Generates a list of all possible combinations from multiple choice questions"""
    combinations_list = list(combinations(options, 1))
    if len(options) > 1:
        for i in range(2, len(options)+1):
            combinations_list.extend(list(combinations(options, i)))
    return combinations_list

def gen_sim_data(template):
    """Generates a simulated data set as a pandas data frame from a pandas data frame template

    First the user specificies how many rows of simulated data they want, then an empty data
    frame with the same column names as the template is generated. The column names are then
    used to determine what kind of data should be entered into the cells.
    """
    n_col = template.shape[1]
    n_row = raw_input("Please specify the desired number rows for the simulated data")
    n_row = np.int(n_row)

    new_matrix = np.empty([n_row, n_col])
    new_matrix[:, :] = np.nan
    sim_data = pd.DataFrame(new_matrix)
    sim_data.columns = template.columns

    for column in sim_data.columns:
        if template.loc['question_type', column] in ['binary', 'likert']:
            options = extract_response_options(template, column)
            sim_values = np.random.choice(options, n_row)
            sim_data.loc[:, column] = sim_values
        elif template.loc['question_type', column] == 'multiple_choice':
            options = extract_response_options(template, column)
            combinations_list = extract_multiple_choice_combinations(options)
            sim_values = np.random.choice(combinations_list, n_row)
            sim_data.loc[:, column] = [', '.join(value).translate(None, "()'") for value in sim_values]
        elif template.loc['question_type', column] == 'quantity':
            print column
            quantity_mean = raw_input("Pick appropriate mean")
            quantity_sd = raw_input("Pick appropriate standard deviation")
            quantity_mean = np.float(quantity_mean)
            quantity_sd = np.float(quantity_sd)
            sim_values = np.round(np.random.normal(quantity_mean, quantity_sd, n_row), 0)
            sim_data.loc[:, column] = sim_values
        elif template.loc['question_type', column] in ['open', 'open_few_options', 'open_list']:
            sim_data.loc[:, column] = np.repeat('there should be text here', n_row)

    return sim_data

def gen_response_sheet(template):
    """Generates a response sheet as a pandas data frame from a pandas data frame template

    The response sheet is simply a data frame with the questions as column names and the permitted response
    alternatives as rows inside the appropriate columns. It is automatically generated from the template
    data frame."""
    n_col = template.shape[1]
    n_row = 1
    for column in template.columns:
        if template.loc['question_type', column] in ['binary', 'likert']:
            options = extract_response_options(template, column)
            if len(options) > n_row:
                n_row = len(options)
        elif template.loc['question_type', column] == 'multiple_choice':
            options = extract_response_options(template, column)
            combinations_list = extract_multiple_choice_combinations(options)
            if len(combinations_list) > n_row:
                n_row = len(combinations_list)

    new_matrix = np.empty([n_row, n_col])
    new_matrix[:, :] = np.nan
    response_sheet = pd.DataFrame(new_matrix)
    response_sheet.columns = template.columns

    for column in response_sheet.columns:
        if template.loc['question_type', column] in ['binary', 'likert']:
            options = extract_response_options(template, column)
            row = 0
            for option in options:
                response_sheet.loc[row, column] = option
                row +=1
        elif template.loc['question_type', column] == 'multiple_choice':
            options = extract_response_options(template, column)
            row = 0
            combinations_list = extract_multiple_choice_combinations(options)

            for option in combinations_list:
                response_sheet.loc[row, column] = ', '.join(option).translate(None, "()'")
                row +=1
        elif template.loc['question_type', column] == 'quantity':
            response_sheet.loc[0, column] = 'number'
        elif template.loc['question_type', column] == 'date':
            response_sheet.loc[0, column] = 'date, format: day-month-year'
        elif template.loc['question_type', column] == 'time':
            response_sheet.loc[0, column] = 'time, format: hour:minutes'
        else:
            response_sheet.loc[0, column] = 'text'

    return response_sheet

def gen_examples_from_template():
    """Wrapper that loads the template, uses the template to generate the simulated data and the response sheet
    and and saves the simulated data and the response sheet to a location the user specifies. """

    template = load_template()
    sim_data = gen_sim_data(template)
    response_sheet = gen_response_sheet(template)

    sim_data_path = raw_input("Where to you want to save the simulated data?")
    response_sheet_path = raw_input("Where to you want to save the response sheet?")

    sim_data.to_csv(sim_data_path, index=False)
    response_sheet.to_csv(response_sheet_path, index=False)

gen_examples_from_template()
