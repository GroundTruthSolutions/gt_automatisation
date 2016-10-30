This repository contains a set of Python functions that are used in the data analysis workflow of Ground Truth Solutions
(http://groundtruthsolutions.org/).

gen_templates.py contains the tool to generate a template csv-file for one particular dataset.
The template file specifies what labels we want for the various questions, what section of the questionnaire
a particular question belongs to, and what type of data we expect for the responses of a given question.
For likert scale questions, binary questions and multiple choice questions the template file also specifies
what response alternatives appropriate for a given question, and how we would expect them to be encoded.
The template file also has a line for what HXL tag we would expect for a specific question, but HXL tags
are not yet implemented in our workflow so that line is currently empty.

gen_examples.py use the template file described above to generate a response sheet, that contains the correctly formated
question labels as well as the allowed respose options for each question. gen_examples.py also contains functions to
simulate data that corresponds to the information in the template file. Both the simulated data and the response sheet
is intended to aid our partners who collect the data, so that they understand how we would like the data to be formatted
when it is sent to us.

Finally, data_cleaning_and_plotting_functions.py is a set of functions that use a template file (as described above)
and a data file to quickly clean, and summarise data both in a tabular format in an excel file and as plot.
We load data_cleaning_and_plotting_functions.py into an interactive Python environment such as Jupyter
(http://jupyter.org/) and then using the functions to speed up descriptive data analysis of the incoming data sets.

The files in this repository rely on a few popular python libararies, it was written to work with the following versions:
numpy 1.11.1
pandas 0.18.1
matplotlib 1.5.3
seaborn 0.7.1
itertools 9.7.0

This code is written and maintained by Tomas Folke. If you have any questions you can reach him at
tomas@groundtruthsolutions.org.