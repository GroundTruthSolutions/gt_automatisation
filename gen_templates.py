__author__ = 'Tomas'
import numpy as np
import pandas as pd

def input_questions():
    question_list = []
    done = False
    while done == False:
        response = response = raw_input("Please input question. Type 'end' when you are finished.")
        if response == 'end':
            done = True
        else:
            question_list.append(response)
    return question_list


def assign_question_sections(questions):
    questionnaire_sections = ['demograpic_data', 'collection_info', 'main_questions']
    section_list = []
    for question in questions:
        if ((question[0] == 'D') | (question[0] == 'd')):
            section_list.append(questionnaire_sections[0])
        elif ((question[0] == 'A') | (question[0] == 'a')):
            section_list.append(questionnaire_sections[1])
        elif ((question[0] == 'Q') | (question[0] == 'q')):
            section_list.append(questionnaire_sections[2])
        else:
            print question
            section_list.append(np.nan)
    return section_list

def assign_question_types(questions):
        question_types = {1:'open', 2:'open_few_options', 3:'quantity', 4:'multiple_choice',
                          5:'likert', 6:'binary' , 7:'date', 8:'time', 9:'other'}
        question_type_list = []
        for question in questions:
            if 'Q' != question[0] and 'sex' in question.split('_'):
                question_type_list.append('binary')
                print question
                print 'binary'
            elif 'Q' != question[0] and 'name' in question.split('_'):
                question_type_list.append('open')
                print question
                print 'open'
            elif 'A' == question[0] and 'time' in question.split('_'):
                question_type_list.append('time')
                print question
                print 'time'
            elif 'A' == question[0] and 'date' in question.split('_'):
                question_type_list.append('date')
                print question
                print 'date'
            elif 'Q' != question[0] and any([word in set(question.split('_')) for word in ['region', 'zone', 'woreda', 'camp_zone', 'division']]):
                question_type_list.append('open_few_options')
                print question
                print 'open_few_options'
            elif 'Q' == question[0] and question.split('_')[0][-1] == 'b':
                question_type_list.append('open')
                print question
                print 'open'
            else:
                print question
                print question_types
                response = raw_input("Please input question type:")
                while response not in [np.str(n) for n in range(1, 10)]:
                    print 'Invalid response, please pick a number between 1 and 9.'
                    response = raw_input("Please input question type:")
                response = np.int(response)
                question_type_list.append(question_types[response])
        return question_type_list


def add_response_options(df):
    binary_options_dict = {1:['1_yes', '2_no'], 2:['1_female', '2_male'], 3:['Other']}
    likert_options_dict = {1:['1_not_at_all', '2_slightly', '3_moderately', '4_nearly', '5_completely', '6_dont_know'],
                           2: ['1_never', '2_rarely', '3_sometimes', '4_most_of_the_time', '5_always', '6_dont know'],
                           3:['Other']}
    response_options_list = []

    for question in df.columns:
        if df.loc[2, question] == 'binary':
            if 'Q' != question[0] and 'sex' in question.split('_'):
                response_options_list.append(['1_female', '2_male'])
                print question
                print ['1_female', '2_male']
            else:
                print question
                print binary_options_dict
                response = raw_input("Please input response type:")

                while response not in [np.str(n) for n in range(1, len(binary_options_dict)+1)]:
                    print 'Invalid response, please pick a number corresponding to one of the options above'
                    response = raw_input("Please input question type:")
                response = np.int(response)
                response_options_list.append(binary_options_dict[response])

        elif df.loc[2, question] == 'likert':
            print question
            print likert_options_dict
            response = raw_input("Please input response type:")

            while response not in [np.str(n) for n in range(1, len(likert_options_dict)+1)]:
                print 'Invalid response, please pick a number corresponding to one of the options above'
                response = raw_input("Please input question type:")

            response = np.int(response)
            response_options_list.append(likert_options_dict[response])

        else:
            response_options_list.append(df.loc[2, question])
            print question
            print df.loc[2, question]

    response_df = pd.DataFrame([response_options_list], columns=df.columns)
    df = df.append(response_df, ignore_index=True)
    return df

def create_template():

    questions = input_questions()

    hxl_tags = [np.nan for n in range(len(questions))]
    section_list = assign_question_sections(questions)
    question_types_list = assign_question_types(questions)
    template = pd.DataFrame([hxl_tags, section_list, question_types_list], columns=questions)
    template = add_response_options(template)

    template.index = ['HXL_tag', 'question_section', 'question_type', 'response_options']

    file_path = raw_input("Where should the template be saved?")

    template.to_csv(file_path)

create_template()
