from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock 
import requests
from kivymd.uix.button import MDRectangleFlatButton
import re
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty, ObjectProperty, ListProperty
import mysql.connector
import pandas as pd
import time
import random

Window.size=(310, 580)

class OptionButton(MDRectangleFlatButton):
    bg_color = ListProperty([1, 1, 1, 1])


class QuizApp(MDApp): 

    selected_topic = ''
    correct_answer= ''
    correct = 0
    wrong = 0

    def build(self):
        global screen_manager 
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file('main.kv'))
        screen_manager.add_widget(Builder.load_file('signup.kv'))
        screen_manager.add_widget(Builder.load_file('login.kv'))
        screen_manager.add_widget(Builder.load_file('topics.kv'))
        screen_manager.add_widget(Builder.load_file('irrigation.kv'))
        screen_manager.add_widget(Builder.load_file('engrais.kv'))
        screen_manager.add_widget(Builder.load_file('semence.kv'))
        screen_manager.add_widget(Builder.load_file('pesticides.kv'))
        screen_manager.add_widget(Builder.load_file('machinisme.kv'))
        screen_manager.add_widget(Builder.load_file('materiel.kv'))
        screen_manager.add_widget(Builder.load_file('final_score.kv')) 
        return screen_manager

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  
    database = mysql.connector.connect(host="127.0.0.1", user="root", password="P@ssw0rd171295",database="login")
    cursor = database.cursor()
    NUM_QUESTIONS_PER_QUIZ = 1

    def wait(self, alert):
        time.sleep(4)
        alert.text=""

    def get_q_by_topic_Id(self,id):
        Qdatabase = mysql.connector.connect(host="127.0.0.1", user="root", password="P@ssw0rd171295",database="quizz")
        Qcursor = Qdatabase.cursor()
        Qcursor.execute(f"select c.topic, b.question, a.answer, d.alternative from quiz_answer a, quiz_question b, quiz_topic c, quiz_alternative d where c.id='{id}' and b.topic_id=c.id and b.id=a.question_id and b.id=d.question_id")
        result = Qcursor.fetchall()
        df = pd.DataFrame(result, columns =['Topic', 'Question','Answer','Alternative'])
        groupby_column = 'Question'
        aggregate_column = 'Alternative'
        agg_df = df.groupby(groupby_column).aggregate({aggregate_column: ','.join})
        df_alias = df.drop(columns=aggregate_column).set_index(groupby_column)
        agg_df=agg_df.join(df_alias).reset_index(groupby_column).drop_duplicates(groupby_column).reset_index(drop=True)
        dfr = agg_df[['Question','Alternative','Answer']].copy()
        dfr["Alternative"] = dfr[['Alternative', 'Answer']].agg(','.join, axis=1)
        dfrl = dfr[['Question','Alternative']].copy()
        #dfrl["Alternative"] = dfrl["Alternative"].str.split(',')
        # The answer will be stored in the last index of the Alternative list
        dfrl = dfrl.groupby(groupby_column).aggregate({aggregate_column:list}).reset_index(drop=False)
        dfrl = dfrl.explode('Alternative')
        dfrl.reset_index(drop=True, inplace=True)
        dfrl = dfrl.astype({'Alternative':'string'})
        df =dfrl.assign(Alternative=dfrl.Alternative.str.split(',')).explode('Alternative').reset_index(drop=True)
        df['Alternative'] = df['Alternative'].str.strip()
        df = df.astype({'Alternative':'string'})
        df1 = df.groupby(groupby_column).aggregate({aggregate_column:list}).reset_index(drop=False)
        df1 = dict(zip(df1['Question'], df1['Alternative']))
        return df1
    
    def prepare_questions(self,questions, num_questions):
        num_questions = min(num_questions, len(questions))
        return random.sample(questions.items(), k=num_questions)

    def select_topic(self,topic):
        self.selected_topic = topic
        if topic == "irrigation":
            quiz_questions = self.get_q_by_topic_Id(1)
        elif topic == "semence":
            quiz_questions= self.get_q_by_topic_Id(2)
        elif topic == "materiel":
            quiz_questions= self.get_q_by_topic_Id(3)
        elif topic == "pesticides":
            quiz_questions= self.get_q_by_topic_Id(4)
        elif topic == "engrais":
            quiz_questions= self.get_q_by_topic_Id(5)
        elif topic == "machinisme":
            quiz_questions= self.get_q_by_topic_Id(6)

        questions = self.prepare_questions(
        quiz_questions, num_questions=self.NUM_QUESTIONS_PER_QUIZ)
        for question, alternatives in questions:
            screen_manager.get_screen(topic).ids.question.text = f"{question}"
            self.correct_answer = alternatives[3]
            for i, alternative in enumerate(sorted(alternatives)):
                    if i == 0:
                        screen_manager.get_screen(topic).ids[f"option{i+1}"].text = f"{alternative}"
                    elif i == 1:
                        screen_manager.get_screen(topic).ids[f"option{i+1}"].text = f"{alternative}"
                    elif i == 2:
                        screen_manager.get_screen(topic).ids[f"option{i+1}"].text = f"{alternative}"
                    elif i == 3:
                        screen_manager.get_screen(topic).ids[f"option{i+1}"].text = f"{alternative}"
        screen_manager.current = topic
        print(topic)
    
    def get_id(self, instance):
        for id, widget in instance.parent.parent.parent.parent.parent.ids.items():
            if widget.__self__ == instance:
                return id

    def quiz(self, option, instance):
        if option == self.correct_answer : 
            self.correct += 1
            screen_manager.get_screen(self.selected_topic).ids[self.get_id(instance)].md_bg_color = (33/255, 189/255, 73/255, 1)
            screen_manager.get_screen(self.selected_topic).ids.resp.color = "green"
            screen_manager.get_screen(self.selected_topic).ids.resp.text = f" Correct ! "
            option_id_list = ["option1","option2","option3","option4"]
            option_id_list.remove(self.get_id(instance))
            # for i in range(0,3):
            #     screen_manager.get_screen(self.selected_topic).ids[f"{option_id_list[i]}"].disabled = True
            #     screen_manager.get_screen(self.selected_topic).ids[f"{option_id_list[i]}"].disabled_color = (0.8,0.8,0.8,1)
        
        else : 
            self.wrong += 1
            for i in range(1,5):
                if screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].text == self.correct_answer :
                    screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].md_bg_color = (33/255, 189/255, 73/255, 1)
                    
                else:
                    screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].disabled = True
                    screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].md_bg_color = (1, 0, 0, 1)

            screen_manager.get_screen(self.selected_topic).ids[self.get_id(instance)].md_bg_color = (1, 0, 0, 1)
            screen_manager.get_screen(self.selected_topic).ids[self.get_id(instance)].disabled_color = (1, 0, 0, 1)
            screen_manager.get_screen(self.selected_topic).ids.resp.text = f" The correct answer is\n{self.correct_answer}"
            screen_manager.get_screen(self.selected_topic).ids.resp.color = "red"
        print(option,  self.get_id(instance))
        

    def next_question(self):
        self.select_topic(self.selected_topic)
        for i in range(1,5):
            screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].disabled = False
            screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].md_bg_color = (206/255, 231/255, 232/255, 1)
            screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].disabled_color = (1, 1, 1, 0.9)
            screen_manager.get_screen(self.selected_topic).ids.resp.text = f""
    
    def final_score(self):
        corr = 0
        wr = 0
        if self.correct == 0 and self.wrong == 0:
            screen_manager.current = "topics"
        else:
            for i in range(1,5):
                screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].disabled = False
                screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].md_bg_color = (206/255, 231/255, 232/255, 1)
                screen_manager.get_screen(self.selected_topic).ids[f"option{i}"].disabled_color = (1, 1, 1, 0.3)
                screen_manager.get_screen(self.selected_topic).ids.resp.text = f""
            if self.selected_topic == "irrigation":
                success_rate = round((self.correct/(self.correct+self.wrong))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{self.correct}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{self.wrong}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"
            elif self.selected_topic == "engrais":
                corr = round(self.correct / 2)
                wr = round(self.wrong / 2)
                success_rate = round((corr/(corr+wr))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{corr}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{wr}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"
            elif self.selected_topic == "semence":
                corr = round(self.correct / 3)
                wr = round(self.wrong / 3)
                success_rate = round((corr/(corr+wr))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{corr}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{wr}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"
            elif self.selected_topic == "pesticides":
                corr = round(self.correct / 4)
                wr = round(self.wrong / 4)
                success_rate = round((corr/(corr+wr))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{corr}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{wr}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"
            elif self.selected_topic == "machinisme":
                corr = round(self.correct / 5)
                wr = round(self.wrong / 5)
                success_rate = round((corr/(corr+wr))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{corr}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{wr}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"
            elif self.selected_topic == "materiel":
                corr = round(self.correct / 6)
                wr = round(self.wrong / 6)
                success_rate = round((corr/(corr + wr))*100)
                screen_manager.get_screen("final_score").ids.correct.text = f"{corr}  Correct !"
                screen_manager.get_screen("final_score").ids.wrong.text = f"{wr}  Wrong !"
                screen_manager.get_screen("final_score").ids.success_rate.text = f"{success_rate}% Success !"
                screen_manager.current = "final_score"

    def replay(self):
        if self.correct > 0 or self.wrong > 0:
            self.correct = 0
            self.wrong = 0
            screen_manager.get_screen("final_score").ids.correct.text = f""
            screen_manager.get_screen("final_score").ids.wrong.text = f""
            screen_manager.get_screen("final_score").ids.success_rate.text = f""
            screen_manager.current = self.selected_topic
        else:
            screen_manager.current = self.selected_topic

    def choose_topic(self):
        if self.correct > 0 or self.wrong > 0:
            self.correct = 0
            self.wrong = 0
            screen_manager.get_screen("final_score").ids.correct.text = f""
            screen_manager.get_screen("final_score").ids.wrong.text = f""
            screen_manager.get_screen("final_score").ids.success_rate.text = f""
            screen_manager.current = "topics"
        else:
            screen_manager.current = "topics"

    # def run_quiz(self,irrig_ques_lab,irrig_alt,irrig_alte,irrig_alter,irrig_altern,alert):     
    #     SemenceQ = self.get_q_by_topic_Id(2)
    #     questions = self.prepare_questions(
    #     SemenceQ, num_questions=self.NUM_QUESTIONS_PER_QUIZ)
    #     num_correct = 0
    #     for question, alternatives in questions:
    #         irrig_ques_lab.text = f"{question}"
    #         correct_answer = alternatives[3]
    #         for i, alternative in enumerate(sorted(alternatives)) :
    #             if i == 0:
    #                 irrig_alt.text = f"{alternative}"
    #             elif i == 1:
    #                 irrig_alte.text = f"{alternative}"
    #             elif i == 2:
    #                 irrig_alter.text = f"{alternative}"
    #             elif i == 3:
    #                 irrig_altern.text = f"{alternative}"
            # user_answer = answer
            # if user_answer == correct_answer:
            #     print(f" Correct! ")
            # elif user_answer == "" :
            #     print(f"The answer is {user_answer!r}")
            # else:    
            #     print(f"The answer is {user_answer!r}")
                                   
        #user_answer = self.select_answer(answer)
        #     if user_answer == correct_answer:
        #         num_correct += 1
        #         print(f"⭐ Correct! ⭐")
        #     else:
        #         print(f"The answer is {correct_answer!r}")

        # print(f"\nYou got {num_correct} correct out of {num} questions")


    

    def send_data(self, username, email, password, alert):
        
        def check_mail_exist(email):
            response = requests.get(
                "https://isitarealemail.com/api/email/validate",
                params = {'email': email})

            status = response.json()['status']
        
            return status
            #returns valid or invalid

        def check_conf(email):
            
            if(re.fullmatch(self.regex, email)):
                return "valid"
            else:
                return "invalid"

        def ch_pass_strenght(password):
            if len(password)>=8 and len(password) < 16 :
                if bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',password))==True :
                    return "valid"
                else:
                    return "weak"
            elif len(password) < 9:
                return "short"    
            else:
                return "long"
                        
        self.cursor.execute("select * from logindata")
        username_list=[]
        email_list=[]

        for i in self.cursor.fetchall():
            username_list.append(i[2])
            email_list.append(i[0])


        conf = check_conf(email.text)
        exst = check_mail_exist(email.text)
        pstr = ch_pass_strenght(password.text)


        if username.text in username_list:
            username.text=""
            alert.text= f"username already exist !"
            
        elif email.text in email_list:
            email.text=""
            alert.text= f"email linked to another user !"    
        
        elif conf == "invalid" :
            email.text=""
            alert.text=f"try a conform email address !"
        
        elif exst == "invalid" :
            email.text=""
            alert.text= f"email does not exist !"
        
        elif pstr == "short":
            password.text=""
            alert.text= f"the password is short !"   

        elif pstr == "weak":
            password.text=""
            alert.text= f"the password is weak !"

        elif pstr == "long":
            password.text=""
            alert.text= f"the password is too long !"   

        else:
            self.cursor.execute(f"insert into logindata values('{email.text}','{password.text}','{username.text}')")
            self.database.commit()
            username.text=""
            email.text=""
            password.text=""
            alert.text= f""

        # if username.text not in username_list and email.text not in email_list and re.fullmatch(regex, email) and status=="valid" and mat==True:
        #     self.cursor.execute("insert into logindata values('{email}','{passwrd}','{username}')")
        #     self.database.commit()
        #     username.text=""
        #     email.text=""
        #     passwrd.text=""

        # elif username.text in username_list and email.text not in email_list and re.fullmatch(regex, email) and status=="valid" and mat==True:          
        #     print("Username already exist")
        
        # elif username.text not in username_list and email.text in email_list and re.fullmatch(regex, email) and status=="valid" and mat==True:
        #     print("email is already matched to a user")

        # elif username.text not in username_list and email.text not in email_list and re.fullmatch(regex, email) and status=="invalid" and mat==True:
        #     print("email does not exist")

        # elif username.text not in username_list and email.text not in email_list and re.fullmatch(regex, email) and status=="valid" and mat==False:
        #     print("Please type a strong password")
        #     # Should have at least one number.
        #     # Should have at least one uppercase and one lowercase character.
        #     # Should have at least one special symbol.
        #     # Should be between 6 to 20 characters long.
        # else:
        #      print("Email not valid")     
        # 
    def validate(self, email, passwor,alert):
        self.cursor.execute("select * from logindata")
        email_list=[]
        for i in self.cursor.fetchall():
            email_list.append(i[0])
        if email.text in email_list and email.text != "":
            self.cursor.execute(f"select pass from logindata where email='{email.text}'")
            for j in self.cursor:
                if passwor.text == j[0]:
                    alert.text= f""
                    passwor.text = ""
                    email.text = ""                    
                else:
                    passwor.text = ""
                    alert.text= f"Incorrect Password !"
        else:
            email.text = ""
            alert.text= f"Incorrect Email"

QuizApp().run()
 