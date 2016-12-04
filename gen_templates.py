
"""gen_templates is a module that generate a template csv file from a questionnaire.

This module is intended to run from the terminal, so that the user copies and pastes the question names into
the terminal and then assigns a question type and responses options to the question. The aim is to make this
manual process automatic by integrating this code into the questionnaire designer at the Feedback Commons.

This module was written to interact with pandas 0.18.1 and numpy 1.11.1.
"""


__version__ = '0.1'
__author__ = 'Tomas Folke'

# import libraries
import numpy as np
import pandas as pd
import os

def input_response_option(options_dict):
    """This function allows the user to select an alternative from a dictionary of options.

    It consists of two parts, it checks if the users input is legal, and if it is legal it
    returns the option as an integer."""
    print options_dict
    response = raw_input("Please input response type:")

    while response not in [np.str(n) for n in options_dict.keys()]:
        print 'Invalid response, please pick a number corresponding to one of the options above'
        response = raw_input("Please input response type:")

    response = np.int(response)
    return response

def input_question_info():
    """ Generates lists of question labels and information pertaining to the labels.

    Specifically, it reformats raw string inputs into the standard structure for GT question labels.
    Then it assigns the question to a specific section of the questionnaire based on the question
    prefix.
    Then it allows the user to select a question type (e.g. open question, likert question,
    multiple choice question, etc.).
    Finally it allows the user to select response options based on question type.
    This process repeats until the user tells the script that all questions have been entered.
    """
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

    experimental = raw_input("If you want to try experimental mode type '1'. If not, please press enter.")
    if(experimental == '1'):
    	return experimental_input_question_info()

    # Loop through the question input cycle until the user specifies that all questions have been added.
    # Once all questions have been added, return the question labels and the information about
    # the questions.
    while done == False:
        question = question = raw_input("Please input question. Type 'end' when you are finished.")
        if question == 'end':
            done = True
            break
        
        question = question.translate(None, "_.,:!?")
        question = question.lower()
        question = '_'.join(question.split())

        # Checking that the question has an appropriate prefix, if not warn the user and ask them to reenter
        # the question.
        if question[0] in ['d', 'a', 'q']:

            questionnaire_sections = ['demographic_data', 'collection_info', 'main_questions']

            # Assign the question to a questionnaire section depending on the question prefix
            if question.startswith('d'):
                question = question.replace("d", 'D', 1)
                section_list.append(questionnaire_sections[0])
            elif question.startswith('a'):
                question = question.replace("a", 'A', 1)
                section_list.append(questionnaire_sections[1])
            elif question.startswith('q'):
                question = question.replace("q", 'Q', 1)
                section_list.append(questionnaire_sections[2])


            print question
            question_list.append(question)
            hxl_tags.append(np.nan)

            print section_list[question_counter]

            question_types = {1:'open', 2:'open_few_options', 3:'open_list',
                4:'quantity', 5:'multiple_choice',
                          6:'likert', 7:'binary' , 8:'date', 9:'time', 10:'other'}

            # Assign some question types automatically, based on keywords in the question names.
            if not question.startswith('Q') and 'sex' in question.split('_'):
                question_type_list.append('binary')
            elif not question.startswith('Q') and 'name' in question.split('_'):
                question_type_list.append('open')
            elif question.startswith('A') and 'time' in question.split('_'):
                question_type_list.append('time')
            elif question.startswith('A') and 'date' in question.split('_'):
                question_type_list.append('date')
            elif not question.startswith('Q') and any([word in set(question.split('_')) for word in ['region', 'zone', 'woreda',
                                            'camp', 'division', 'kakuma', 'block']]):
                question_type_list.append('open_few_options')
            elif question.startswith('Q') and question.split('_')[0][-1] == 'b':
                question_type_list.append('open')

            else:
                response = input_response_option(question_types)

                print question_types[response]
                question_type_list.append(question_types[response])

            binary_options_dict = {1:['1_no', '2_yes', '3_dont_know', '4_dont_want_to_answer'],
                                   2:['1_yes', '2_no', '3_dont_know', '4_dont_want_to_answer'],
                                   3:['1_female', '2_male', '3_other'], 4:['Other']}
            likert_options_dict = {1:['1_not_at_all', '2_slightly', '3_moderately', '4_mostly', '5_completely', '6_dont_know', '7_dont_want_to_answer'],
                                   2:['1_completely', '2_mostly', '3_moderately', '4_slightly', '5_not_at_all', '6_dont_know', '7_dont_want_to_answer'],
                                     3: ['1_never', '2_rarely', '3_sometimes', '4_most_of_the_time', '5_always', '6_dont_know', '7_dont_want_to_answer'],
                                     4: ['1_always', '2_most_of_the_time', '3_sometimes', '4_rarely', '5_never', '6_dont_know', '7_dont_want_to_answer'],
                                        5:['Other']}

            # Assign response options to binary questions
            if question_type_list[question_counter] == 'binary':
                # If the question contains the words 'sex' or 'gender' assign gender response options
                if not question.startswith('Q') and any([word in set(question.split('_')) for word in ['sex', 'gender']]):
                    response_options_list.append(['1_female', '2_male', '3_other'])
                # otherwise let the user pick a response option
                else:
                    response = input_response_option(binary_options_dict)
                    response_options_list.append(binary_options_dict[response])

            # Let the user manually assign response options to likert scale questions
            elif question_type_list[question_counter] == 'likert':
                response = input_response_option(likert_options_dict)
                response_options_list.append(likert_options_dict[response])

            # If the question is an open list create one column per possible list entry
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

            # If the question type is not binary, likert scale or open list just assign the question type
            # to the response options field
            else:
                response_options_list.append(question_type_list[question_counter])

            print response_options_list[question_counter]

            question_counter += 1

        elif question != 'end':
            print 'Does not recognise question format, please re-enter question'

    return [question_list, hxl_tags, section_list, question_type_list, response_options_list]

def get_file_path():
	recomended_file_path = os.getcwd() + "/temp.csv"
	file_path = raw_input("Where should the template be saved? (if left empty : " + recomended_file_path + ")")

	if file_path == "":
		file_path = recomended_file_path

	return file_path

def experimental_input_question_info():

    """ Generates lists of question labels and information pertaining to the labels.

    Specifically, it reformats raw string inputs into the standard structure for GT question labels.
    Then it assigns the question to a specific section of the questionnaire based on the question
    prefix.
    Then it allows the user to select a question type (e.g. open question, likert question,
    multiple choice question, etc.).
    Finally it allows the user to select response options based on question type.
    This process repeats until the user tells the script that all questions have been entered.
    """
	
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
	

    print "Please paste all questions. Press Ctrl+D to generate template."
    
    # Extract all the input into an array
    contents = []
    while True:
    	try:
    		line = raw_input("")
    	except EOFError:
    		break
    	contents.append(line)

       # Loop through the question input cycle until the user specifies that all questions have been added.
       # Once all questions have been added, return the question labels and the information about
       # the questions.
    for question in contents:
    	question = question.translate(None, "_.,:!?")
    	question = question.lower()
    	question = '_'.join(question.split())
    	
    	# Checking that the question has an appropriate prefix, if not warn the user and ask them to reenter
    	# the question.
    	
    	if question == "":
    		continue
    	if not question[0] in ['d', 'a', 'q']:
    		print "Error! Dould not parse question: " + question
    		return experimental_input_question_info()
    	questionnaire_sections = ['demographic_data', 'collection_info', 'main_questions']
           # Assign the question to a questionnaire section depending on the question prefix
    	if question.startswith('d'):
    		question = question.replace("d", 'D', 1)
    		section_list.append(questionnaire_sections[0])
    	elif question.startswith('a'):
    		question = question.replace("a", 'A', 1)
    		section_list.append(questionnaire_sections[1])
    	elif question.startswith('q'):
    		question = question.replace("q", 'Q', 1)
    		section_list.append(questionnaire_sections[2])
    	
    	
    	print "Working on question: " + question
    	question_list.append(question)
    	hxl_tags.append(np.nan)
    	
    	question_types = {1:'open', 2:'open_few_options', 3:'open_list',
               4:'quantity', 5:'multiple_choice',
                         6:'likert', 7:'binary' , 8:'date', 9:'time', 10:'other'}
           # Assign some question types automatically, based on keywords in the question names.
    	if not question.startswith('Q') and 'sex' in question.split('_'):
    		question_type_list.append('binary')
    	elif not question.startswith('Q') and 'name' in question.split('_'):
    		question_type_list.append('open')
    	elif question.startswith('A') and 'time' in question.split('_'):
    		question_type_list.append('time')
    	elif question.startswith('A') and 'date' in question.split('_'):
    		question_type_list.append('date')
    	elif not question.startswith('Q') and any([word in set(question.split('_')) for word in ['region', 'zone', 'woreda',
                                           'camp', 'division', 'kakuma', 'block']]):
    		question_type_list.append('open_few_options')
    	elif question.startswith('Q') and question.split('_')[0][-1] == 'b':
    		question_type_list.append('open')
    	else:
    		response = input_response_option(question_types)
    		
    		print question_types[response]
    		question_type_list.append(question_types[response])
    	binary_options_dict = {1:['1_no', '2_yes', '3_dont_know', '4_dont_want_to_answer'],
                                  2:['1_yes', '2_no', '3_dont_know', '4_dont_want_to_answer'],
                                  3:['1_female', '2_male', '3_other'], 4:['Other']}
    	likert_options_dict = {1:['1_not_at_all', '2_slightly', '3_moderately', '4_mostly', '5_completely', '6_dont_know', '7_dont_want_to_answer'],
                                  2:['1_completely', '2_mostly', '3_moderately', '4_slightly', '5_not_at_all', '6_dont_know', '7_dont_want_to_answer'],
                                    3: ['1_never', '2_rarely', '3_sometimes', '4_most_of_the_time', '5_always', '6_dont_know', '7_dont_want_to_answer'],
                                    4: ['1_always', '2_most_of_the_time', '3_sometimes', '4_rarely', '5_never', '6_dont_know', '7_dont_want_to_answer'],
                                       5:['Other']}
           # Assign response options to binary questions
    	if question_type_list[question_counter] == 'binary':
    		# If the question contains the words 'sex' or 'gender' assign gender response options
    		if not question.startswith('Q') and any([word in set(question.split('_')) for word in ['sex', 'gender']]):
    			response_options_list.append(['1_female', '2_male', '3_other'])
               # otherwise let the user pick a response option
    		else:
    			response = input_response_option(binary_options_dict)
    			response_options_list.append(binary_options_dict[response])
           # Let the user manually assign response options to likert scale questions
    	elif question_type_list[question_counter] == 'likert':
    		response = input_response_option(likert_options_dict)
    		response_options_list.append(likert_options_dict[response])
           # If the question is an open list create one column per possible list entry
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
           # If the question type is not binary, likert scale or open list just assign the question type
           # to the response options field
    	else:
    		response_options_list.append(question_type_list[question_counter])
    	question_counter += 1
    return [question_list, hxl_tags, section_list, question_type_list, response_options_list]

def create_template():
    """ Wrapping function to create the template and save it as a csv file.

    Runs the input_question_function, use the output to create a pandas data frame.
    Saves the data frame where the user specifies.
    """

    question_info = input_question_info()

    template = pd.DataFrame(question_info[1:], columns=question_info[0])

    template.index = ['HXL_tag', 'question_section', 'question_type', 'response_options']

    file_path = get_file_path()
    template.to_csv(file_path)

create_template()
