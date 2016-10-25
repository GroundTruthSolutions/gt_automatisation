__author__ = 'Tomas'
import numpy as np
import pandas as pd

def input_response_option(options_dict):
    print options_dict
    response = raw_input("Please input response type:")

    while response not in [np.str(n) for n in options_dict.keys()]:
        print 'Invalid response, please pick a number corresponding to one of the options above'
        response = raw_input("Please input response type:")

    response = np.int(response)
    return response

def input_question_info():
    question_list = []
    section_list = []
    question_type_list = []
    response_options_list = []
    hxl_tags = []

    done = False

    question_counter = 0
    demographic_counter = 0
    main_counter = 0
    meta_counter = 0
    while done == False:
        question = question = raw_input("Please input question. Type 'end' when you are finished.")
        if question == 'end':
            done = True
        else:
            question = question.translate(None, ".,:!?")
            question = question.lower()
            question = '_'.join(question.split())

        if question[0] in ['d', 'a', 'q']:

                questionnaire_sections = ['demographic_data', 'collection_info', 'main_questions']

                if (question[0] == 'd'):
                    question = question.replace("d", 'D', 1)
                    section_list.append(questionnaire_sections[0])
                elif (question[0] == 'a'):
                    question = question.replace("a", 'A', 1)
                    section_list.append(questionnaire_sections[1])
                elif (question[0] == 'q'):
                    question = question.replace("q", 'Q', 1)
                    section_list.append(questionnaire_sections[2])


                print question
                question_list.append(question)
                hxl_tags.append(np.nan)

                print section_list[question_counter]

                question_types = {1:'open', 2:'open_few_options', 3:'open_list',
                    4:'quantity', 5:'multiple_choice',
                              6:'likert', 7:'binary' , 8:'date', 9:'time', 10:'other'}

                if 'Q' != question[0] and 'sex' in question.split('_'):
                    question_type_list.append('binary')
                elif 'Q' != question[0] and 'name' in question.split('_'):
                    question_type_list.append('open')
                elif 'A' == question[0] and 'time' in question.split('_'):
                    question_type_list.append('time')
                elif 'A' == question[0] and 'date' in question.split('_'):
                    question_type_list.append('date')
                elif 'Q' != question[0] and any([word in set(question.split('_')) for word in ['region', 'zone', 'woreda',
                                                'camp', 'division', 'kakuma', 'block']]):
                    question_type_list.append('open_few_options')
                elif 'Q' == question[0] and question.split('_')[0][-1] == 'b':
                    question_type_list.append('open')

                else:
                    response = input_response_option(question_types)

                    print question_types[response]
                    question_type_list.append(question_types[response])

                binary_options_dict = {1:['1_no', '2_yes', '3_dont_know', '4_dont_want_to_answer'],
                                       2:['1_yes', '2_no', '3_dont_know', '4_dont_want_to_answer'],
                                       3:['1_female', '2_male'], 4:['Other']}
                likert_options_dict = {1:['1_not_at_all', '2_slightly', '3_moderately', '4_mostly', '5_completely', '6_dont_know', '7_dont_want_to_answer'],
                                       2:['1_completely', '2_mostly', '3_moderately', '4_slightly', '5_not_at_all', '6_dont_know', '7_dont_want_to_answer'],
                                         3: ['1_never', '2_rarely', '3_sometimes', '4_most_of_the_time', '5_always', '6_dont_know', '7_dont_want_to_answer'],
                                         4: ['1_always', '2_most_of_the_time', '3_sometimes', '4_rarely', '5_never', '6_dont_know', '7_dont_want_to_answer'],
                                            5:['Other']}

                if question_type_list[question_counter] == 'binary':
                    if 'Q' != question[0] and any([word in set(question.split('_')) for word in ['sex', 'gender']]):
                        response_options_list.append(['1_female', '2_male'])
                    else:
                        response = input_response_option(binary_options_dict)
                        response_options_list.append(binary_options_dict[response])

                elif question_type_list[question_counter] == 'likert':
                    response = input_response_option(likert_options_dict)
                    response_options_list.append(likert_options_dict[response])
                elif question_type_list[question_counter] == 'open_list':
                    response = raw_input('How many instances does the list have?')
                    response = np.int(response)
                    if response > 1:
                        question_list_labels = []
                        for i in range(1, response+1):
                            words = question.split('_')
                            words[0] = words[0]+'-%d' %i
                            label = '_'.join(words)
                            question_list_labels.append(label)
                        question_list[question_counter] = question_list_labels[0]
                        response_options_list.append(question_type_list[question_counter])
                        for label in question_list_labels[1:]:
                            question_list.append(label)
                            hxl_tags.append(np.nan)
                            section_list.append(section_list[question_counter])
                            question_type_list.append('open_list')
                            response_options_list.append('open_list')
                            question_counter += 1

                else:
                    response_options_list.append(question_type_list[question_counter])

                print response_options_list[question_counter]

                question_counter += 1

        elif question != 'end':
            print 'Does not recognise question format, please re-enter question'

    return [question_list, hxl_tags, section_list, question_type_list, response_options_list]


def create_template():

    question_info = input_question_info()

    template = pd.DataFrame(question_info[1:], columns=question_info[0])

    template.index = ['HXL_tag', 'question_section', 'question_type', 'response_options']

    file_path = raw_input("Where should the template be saved?")

    template.to_csv(file_path)

create_template()
