from kivy.uix.screenmanager import ScreenManager, Screen
import pickle
from kivymd.app import MDApp as App
from kivymd.uix.gridlayout import MDGridLayout as GridLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView as ScrollView
from kivymd.uix.button import MDFillRoundFlatButton as Button
from kivymd.uix.label import MDLabel as Label
from kivymd.uix.textfield import MDTextField as TextInput
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.theming import ThemeManager
from kivy.uix.image import Image
import random
import re
import torch
import torch.nn as nn
device = 'cpu'

Q = {
    'age':[['Hi, \nwelcome to Heartily. \nLet\'s start by asking your age.', 'Hi there ! \nHow old are you?', 'Hello, \nwhat is your age?'], 
           ['Enter your age here', 'Type in your age']],
    
    'gender':[['Are you male or female?', 'Hi, please select your gender.', 'What is your gender?'], 
           ['Answer with \'male\' or \'female\'']],
    
    'cp':[['What type of chest pain do you have?', 'Could you describe your chest pain?', 'What kind of chest pain are you experiencing?'], 
          ['0 for typical angina, 1 for atypical angina, 2 for non-anginal pain, 3 for asymptomatic', 'Enter 0 for typical angina, 1 for atypical angina, 2 for non-anginal pain, or 3 for asymptomatic chest pain', 'Chest Pain Type (0-3)']],
    
    'thalach':[['What is your maximum heart rate?', 'How high can your heart rate go?', 'What is the highest heart rate you\'ve achieved?'], 
                ['Enter your maximum heart rate here', 'Maximum Heart Rate']],
    
    'exang':[['Do you experience exercise-induced angina?', 'Do you feel chest pain during exercise?', 'Have you experienced chest pain during exercise?'], 
             ['Answer with \'Yes\' or \'No\'']],
    
    'oldpeak':[['How much ST depression did you experience relative to rest?', 'What is your ST depression score?', 'Please enter your ST depression score.'], 
               ['Enter your ST depression score here']],
    
    'slope':[['What is the slope of your peak exercise ST segment?', 'How would you describe the slope of your peak exercise ST segment?', 'Please indicate the slope of your peak exercise ST segment.'], 
             ['0 for upsloping, 1 for flat, 2 for downsloping', 'Enter 0 for upsloping, 1 for flat, or 2 for downsloping', 'Peak Exercise ST Segment Slope (0-2)']],
    
    'ca':[['How many major vessels have been colored by fluoroscopy?', 'What is the count of colored major vessels by fluoroscopy?', 'Please enter the count of colored major vessels by fluoroscopy.'], 
          ['Enter the count of colored major vessels here', 'Count of colored major vessels']],
    
    'thal':[['What is your thalassemia diagnosis?', 'Have you been diagnosed with thalassemia?', 'Please indicate your thalassemia diagnosis.'], 
            ['Answer with 0 for error, 1 for fixed defect, 2 for normal, 3 for reversible defect', ]]
}
ans = {}


#Copy of the net
class neuralnet(nn.Module):
    def __init__(self,input_dim,output_dim):
        super(neuralnet,self).__init__()
        self.layer1 = nn.Linear(input_dim,input_dim*4)
        self.dropout1 = nn.Dropout(0.2)
        self.layer2 = nn.Linear(input_dim*4,input_dim*10)
        self.dropout2 = nn.Dropout(0.2)
        self.layer3 = nn.Linear(input_dim*10,input_dim*6)
        self.dropout3 = nn.Dropout(0.2)
        self.layer4 = nn.Linear(input_dim*6,input_dim*4)
        self.layertmp = nn.Linear(input_dim,input_dim*4)
        self.norm = nn.LayerNorm(input_dim*4)

        self.layer5 = nn.Linear(input_dim*4,output_dim)
        self.af = nn.GELU()

        self.loss=nn.BCELoss()

    def forward(self,x,y=None):

        if(y==None):
            with torch.no_grad():

                tmp = x
                out = self.layer1(x)
                out = self.layer2(out)
                out = self.af(out)
                out = self.layer3(out)
                out = self.af(out)
                out = self.layer4(out)
                out = self.af(out)

                tmp = self.layertmp(tmp)
                tmp = self.norm(tmp)
                
                out = out + tmp
                out = self.layer5(out)
                out = torch.sigmoid(out)


                return out
        else:
            
            tmp = x
            out = self.layer1(x)
            out = self.layer2(out)
            out = self.af(out)
            out = self.dropout1(out)
            out = self.layer3(out)
            out = self.af(out)
            out = self.dropout2(out)
            out = self.layer4(out)
            out = self.af(out)
            out = self.dropout3(out)

            tmp = self.layertmp(tmp)
            tmp = self.norm(tmp)
            
            out = out + tmp
            out = self.layer5(out)

            out = torch.sigmoid(out)

            error = self.loss(out,y)

            return out,error

class Logo(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.next_screen = 'age'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #Image
        self.image = Image(source='Heartly_LOGO.png',size_hint=(0.9, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})
        layout.add_widget(self.image)

        #The submit button
        self.submit_button = Button(text='Go', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        self.manager.current = self.next_screen

class AgeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'age'
        self.next_screen = 'gender'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class GenderScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'gender'
        self.next_screen = 'cp'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = self.input.text
        if(out == ''):
            out = 'female'
        else:
            out = out.lower()

        if('female' in out):
            ans[self.key] = 0
        else:
            ans[self.key] = 1

        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class CpScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'cp'
        self.next_screen = 'thalach'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class ThalachScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'thalach'
        self.next_screen = 'exang'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class ExangScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'exang'
        self.next_screen = 'oldpeak'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = self.input.text
        if(out == ''):
            out = 'no'
        else:
            out = out.lower()

        if('yes' in out):
            ans[self.key] = 1
        else:
            ans[self.key] = 0

        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class OldpeakScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'oldpeak'
        self.next_screen = 'slope'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class SlopeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'slope'
        self.next_screen = 'ca'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class CaScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'ca'
        self.next_screen = 'thal'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)
        print("Debug : Updated Struct -->",ans)
        self.manager.current = self.next_screen

class ThalScreen(Screen):

    def __init__(self,res,**kwargs):
        super().__init__(**kwargs)

        global Q
        self.res = res
        self.key = 'thal'
        self.next_screen = 'result'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text=random.choice(Q[self.key][0]))
        self.text.font_size=27
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The Actualinput
        self.input = TextInput(text=random.choice(Q[self.key][1]), multiline=False)
        layout.add_widget(self.input)

        #The submit button
        self.submit_button = Button(text='Next', on_press=self.next,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "y": 0})
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        global ans

        out = re.findall(r'\d+\.?\d*', self.input.text)
        if(len(out) == 0):
            out = 0
        else:
            out = out[0]

        ans[self.key] = float(out)

        if('ans' in ans):
            del ans['ans']

        model = torch.load('MLP Heart Disease\engine_nn.CookieNeko').to(device)
        give = torch.tensor([list(ans.values())],dtype=torch.float32)
        print(give)
        
        final = float(model(give))

        ans['ans'] = final


        print("Debug : Updated Struct -->",ans)
        self.res.update()
        self.manager.current = self.next_screen

class ResultScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global Q
        self.key = 'thal'
        self.next_screen = 'logo'
        #Layout
        layout = GridLayout(cols=1, spacing=30)
        layout.size_hint = (0.9,0.8)
        layout.pos_hint = {"center_x":0.5, "center_y":0.5}
        layout.padding = [30,0,30,50]

        #The writing, label
        self.text = Label(text="")
        self.text.font_size=35
        self.text.color = (1,0.4,0.4)
        layout.add_widget(self.text)

        #The submit button
        self.submit_button = Button(text='Try Again', on_press=self.next,size_hint = (0.3,0.1), pos_hint={"center_x": 0.1, "y": 0})
        self.submit_button.size = [0.1,0.1]
        layout.add_widget(self.submit_button)

        #Attach everything
        self.add_widget(layout)

    #Switch to the next screen
    def next(self,instance):

        self.manager.current = self.next_screen

    def update(self):
        per = ans['ans']*100
        self.text.text = "You have "+str(per)[:5]+"% probability of having a Heart Disease. \nTake good care."


class HeartDiseaseAppPredictor(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.theme_cls.primary_palette="Red"

        # create screens for each input field
        logo_screen = Logo(name='logo')
        age_screen = AgeScreen(name='age')
        gender_screen = GenderScreen(name='gender')
        cp_screen = CpScreen(name='cp')
        thallach_screen = ThalachScreen(name='thalach')
        exang_screen = ExangScreen(name ='exang')
        oldpeak_scren = OldpeakScreen(name ='oldpeak')
        slope_screen = SlopeScreen(name='slope')
        ca_screen = CaScreen(name='ca')
        result_screen = ResultScreen(name='result')
        thal_screen = ThalScreen(res = result_screen, name = 'thal')

        # add similar screens for each input field

        self.screen_manager.add_widget(logo_screen)
        self.screen_manager.add_widget(age_screen)
        self.screen_manager.add_widget(gender_screen)
        self.screen_manager.add_widget(cp_screen)
        self.screen_manager.add_widget(thallach_screen)
        self.screen_manager.add_widget(exang_screen)
        self.screen_manager.add_widget(oldpeak_scren)
        self.screen_manager.add_widget(slope_screen)
        self.screen_manager.add_widget(ca_screen)
        self.screen_manager.add_widget(thal_screen)
        self.screen_manager.add_widget(result_screen)

        # add similar screens for each input field

        return self.screen_manager

if __name__ == '__main__':
   HeartDiseaseAppPredictor().run()