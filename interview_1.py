import sys
import re
import logging
import random
import yaml
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# print things to the command window
def trace(string):
    sys.stderr.write(string+'\n')
    sys.stderr.flush()
    return

app = Flask(__name__)
ask = Ask(app, "/")

neg = 0
pos = 0
emp = 0



def rating():
    global pos, neg, emp
    session.attributes['rating'] = 0 #rating starts at 0 points
    neg_r = 0.75 * neg
    pos_r = 1 * pos
    emp_r = emp * 0.25
    session.attributes['rating'] = pos_r - neg_r - emp_r
    ratings = session.attributes['rating']
    round_msg = 'You used ' + str(pos) + ' positive words, ' + str(neg) + ' negative words, and ' +str(emp) +' empty words in your interview. Your score was a ' + str(ratings) +'.'
    if ratings >= 3:
        return round_msg + ' You had a pretty positive interview!'
    if ratings <= -2:
        return round_msg + ' You used more negative and empty words than positive words by a wide margin. Try to be a tad bit more positive in your actual interview.'
    if -2 < ratings < 3:
        return round_msg + ' You had an almost equal mix of positive and negative and empty words in your interview. Try to be more positive in your actual interview.'



# first regular expression 'w' and then every time after that do 'a'
@ask.launch
def beginInterview():
    if 'hello' in session.attributes:
        prefix = ''
    else:
        session.attributes['hello'] = 1
    # do I need and sessions?
    with open('questions.yaml') as f:
        questions = yaml.load(f.read())
    session.attributes['state'] = 'Hello' # set state as what you are in
    session.attributes['numberOfQuestions'] = 0
    session.attributes['badWords'] = 0
    session.attributes['goodWords'] = 0
    session.attributes['emptyWords'] = 0
    session.attributes['questionList'] = questions
    session.attributes['question']  = None #question number asked
    #hello_msg = render_template('hello')
    hello_msg = "Welcome to College Interview. Ready to practice?"
    return question(hello_msg) # makes alexa ask question

@ask.intent("AMAZON.YesIntent")
def instructions(Freeform):

    sys.stderr.write('\n-----------------------[OLD state]----> '+str(session.attributes['state'])+'\n')
    sys.stderr.flush()

    # the user bails immediately; i.e. no games were played. Express regret
    if session.attributes['state'] == 'Hello': # origin state
        
        session.attributes['state'] = 'Instruction' # set current state
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
    #instruction_msg = render_template('instruction')
        instruction_msg = "Say Repeat Question to hear the question again, Next Question  to move on, and End Interview to end the interview and receive your feedback. If you are ready, say start my interview."
        return question(instruction_msg)
    
    else:
        session.attributes['state'] = 'Yes Intent Called' # set current state
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
        generateQuestion(Freeform)
        # finish this thing
    
@ask.intent("GreetingIntent")
def greeting():

    if session.attributes['state'] == 'Instruction': # origin state
        
        session.attributes['state'] = 'Greeting' # set current state
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
  #  greeting_msg = render_template('greeting')
    greeting_msg = "Hello, how are you doing today?"
    return question(greeting_msg)


@ask.intent("QuestionIntent")
def generateQuestion(Freeform):
    global pos, neg, emp
    #words = str(scooby)
    if (session.attributes['state'] == 'Greeting' and session.attributes['numberOfQuestions'] == 0):
         session.attributes['state'] = 'Question'
         sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
         sys.stderr.flush()
      #   prefix = render_template('greeting_response')
         greeting_response_msg = "I'm doing well, thank you for asking. Tell me about yourself. "
         session.attributes['numberOfQuestions'] == 1
         return question(greeting_response_msg)
    
    else: 
         session.attributes['state'] = 'Question'
         sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
         sys.stderr.flush()
         questionIndex = random.randint(0,len(session.attributes['questionList'])-1)
         question_msg = session.attributes['questionList'][questionIndex]
         session.attributes['question'] = question_msg
         session.attributes['numberOfQuestions'] += 1
         session.attributes['questionList'].pop(questionIndex)

   #words isn't a thing right now - FIXXXXXX
         record(Freeform)
    return question(question_msg)
   
   
def record(Freeform):
    global pos, neg, emp
    session.attributes['state'] = 'Recording'
    sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
    sys.stderr.flush()
         
    words = Freeform 
    sys.stderr.write('------------------------------------------------------------')
    sys.stderr.write(words +'\n')
    sys.stderr.flush()


    pos_words = ['focus', 'hard-working',  'dedication', 'thank you', 'appreciate', 'diligent', 'motivation', 'initiative', 'grateful', 'determined', 'dynamic', 'mature', 'independent', 'happy', 'enjoy', 'splendid', 'goal', 'interested', 'opportunity', 'individual', 'fortunate', 'incredible', 'inspire', 'influence', 'achieve', 'honest', 'benefit', 'willing', 'effort', 'fantastic', 'balance', 'interact', 'enlightening', 'culture', 'innovation', 'involved', 'leadership']
    neg_words = ['nigger', 'smarter than', 'hate', 'dumb', 'stupid', 'ugly', 'lame', 'weird', 'nasty', 'terrible', 'horrible', 'awful', 'heck', 'darn', 'poop', 'shit', 'fuck', 'damn', 'hell', 'ass', 'bitch', 'cunt', 'cock', 'pussy', 'dick', 'asshole', 'ass', 'safety school', 'backup school', 'sucks', 'blows', 'obsessed', 'shucks', 'drugs', 'alcohol', 'avoid', 'worst', 'desperate', 'failure', 'you know', 'you guys', 'bad']
    emp_words = ['sorry', 'kind of', 'sort of', 'amazing', 'basically', 'kind of', 'actually', 'so', 'stuff', 'sure', 'yeah', 'I don’t know', 'well', 'maybe', 'technically', 'I think', 'mostly', 'wait', 'I guess']
    pos_words = "|".join(pos_words)
    neg_words = "|".join(neg_words)
    emp_words = "|".join(emp_words)
    pos += len(re.findall(pos_words, Freeform))
    neg += len(re.findall(neg_words, Freeform))
    emp += len(re.findall(emp_words, Freeform))

    
@ask.intent("RepeatIntent")
def repeatQuestion():
    if(session.attributes['state'] == 'Recording'):
        session.attributes['state'] = 'Repeat'
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
    return question(session.attributes['question'])


@ask.intent("AMAZON.NoIntent")
def all_done():
    global pos, neg, emp
    sys.stderr.write('\n-----------------------[OLD state]----> '+str(session.attributes['state'])+'\n')
    sys.stderr.flush()

    # the user bails immediately; i.e. no games were played. Express regret
    if session.attributes['state'] == 'Hello': # origin state
        # starement() says something then exists immediately
        session.attributes['state'] = 'Goodbye' # set current state
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
    msg = 'Ah well...you could’ve gotten into college! Maybe next time pal! Goodbye'
    
    if session.attributes['state'] != 'Hello':
        session.attributes['state'] = 'Goodbye2'
        sys.stderr.write('-----------------------[NEW state]----> '+str(session.attributes['state'])+'\n')
        sys.stderr.flush()
    msg = rating()+ " " + 'Well then, I hope you had a nice interview.'

    return statement(msg)


# get the recognition, speak it back and show on the screen

if __name__ == '__main__':
    app.run(debug=True)






