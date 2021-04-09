# Combat-Covid

## Problem statement:
One of the main headlines and problems, related to covid was the amount of burden it put on the current health system and the front-line workers.

## Our Idea:
So, our idea is to work on introducing a covid testing procedure with the power of AI using convolutional neural network, to automatically decide whether the patient has covid or not. We believe that with an appropriate amount of data, deep learning algorithms could automatically analyse computed tomography (CT) of the chest and the clinical history, prioritize radiology worklists, and reduce the time for the diagnosis of COVID-19. 

## Implementation of our idea:
The First and foremost, step is data collection. Data collection is done in two different methods.
One is collecting data using forms. It includes providing very detailed written form in which patient can write their symptoms and our text recognition system gathers the data. The Second one is that the patient can talk about their habits and symptoms and our speech recognition algorithm will gather the data. The Patient can use either way in which they are comfortable.
The application then uses OpenAI to compare the data against many recorded backgrounds and symptoms to give a prediction of the Covid test Result. If there is a high probability of a positive result, the hospital technician can issue a CT scan of the patient's chest. At last, the report of the covid test will be formatted as pdf and sent to the patient through the mail. If the patient gets positive, we also suggest the medication according to their symptoms.
Through this, the patient can know their covid test result without consulting a doctor. 
 
