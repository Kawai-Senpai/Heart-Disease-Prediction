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

class HeartDiseaseAppPredictor(App):

    def build(self):

        self.icon = 'Heartly_BareLOGO.ico'

        self.theme_cls.primary_palette="Red"

        self.model = pickle.load(open('engine.CookieNeko', 'rb'))

        self.image = Image(source='Heartly_LOGO.png',size_hint=(None, None), size=(300, 100), pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.age_input = TextInput(text='Age', multiline=False)
        self.sex_input = TextInput(text='Gender', multiline=False)
        self.cp_input = TextInput(text='Chest Pain', multiline=False)
        self.trestbps_input = TextInput(text='Resting BP', multiline=False)
        self.chol_input = TextInput(text='Cholesterol', multiline=False)
        self.fbs_input = TextInput(text='Fasting BP', multiline=False)
        self.restecg_input = TextInput(text='Resting ECG', multiline=False)
        self.thalach_input = TextInput(text='Max Heart Rate', multiline=False)
        self.exang_input = TextInput(text='EI Angina', multiline=False)
        self.oldpeak_input = TextInput(text='ST Depression', multiline=False)
        self.slope_input = TextInput(text='Slope of STS', multiline=False)
        self.ca_input = TextInput(text='Major Vessels', multiline=False)
        self.thal_input = TextInput(text='Thalassemia', multiline=False)
        self.blank = Label(text='')


        submit_button = Button(text='Submit', on_press=self.submit,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "center_y": 0.5})
        info_button = Button(text='More Info', on_press=self.info,size_hint = (0.9,0.1), pos_hint={"center_x": 0.5, "center_y": 0.5})

        inputs_layout = GridLayout(cols=1, spacing=10)
        inputs_layout.size_hint = (0.9,None)
        inputs_layout.pos_hint = {"center_x":0.5, "center_y":0.5}

        inputs_layout.add_widget(self.image)
        inputs_layout.add_widget(self.age_input)
        inputs_layout.add_widget(self.sex_input)
        inputs_layout.add_widget(self.cp_input)
        inputs_layout.add_widget(self.trestbps_input)
        inputs_layout.add_widget(self.chol_input)
        inputs_layout.add_widget(self.fbs_input)
        inputs_layout.add_widget(self.restecg_input)
        inputs_layout.add_widget(self.thalach_input)
        inputs_layout.add_widget(self.exang_input)
        inputs_layout.add_widget(self.oldpeak_input)
        inputs_layout.add_widget(self.slope_input)
        inputs_layout.add_widget(self.ca_input)
        inputs_layout.add_widget(self.thal_input)

        inputs_layout.add_widget(submit_button)
        inputs_layout.add_widget(info_button)

        inputs_layout.bind(minimum_height=inputs_layout.setter('height'))

        # create a ScrollView and add the GridLayout to it
        scroll_view = ScrollView()
        scroll_view.size_hint = (0.9,0.9)
        scroll_view.pos_hint = {"center_x":0.5, "center_y":0.5}

        scroll_view.add_widget(inputs_layout)

        return scroll_view
    
    def show_popup(self,res,topic):
        dialog = MDDialog(
        title=topic,
        text=res,
        elevation=0,
        size_hint=(0.7, 0.4),
        buttons=[
            MDFlatButton(
                text="Close",
                on_release=lambda *args: dialog.dismiss()
                        )
                ]
            )
        dialog.open()  

    def info(self,instance):
        self.show_popup('''
    Welcome to our app! 
    To use it effectively, you need to know what values to enter in the various fields. 
    Here's a quick guide to help you :

    age: age in years
    sex: sex (1,0)
    cp: chest pain type (0,1,2,3)
    trestbps: resting blood pressure (in mm Hg )
    chol: serum cholestoral in mg/dl
    fbs: ( if fasting blood sugar > 120 mg/dl 1 or 0)
    restecg: resting electrocardiographic results (0,1,2)
    thalach: maximum heart rate achieved
    exang: exercise induced angina (0,1)
    oldpeak: ST depression induced by exercise relative to rest
    slope: the slope of the peak exercise ST segment (0,1,2)
    ca: number of major vessels (0-3) colored by flourosopy
    thal: (0,1,2,3)
''',"Data Dictionary")

    def submit(self, instance):
        age = int(self.age_input.text)
        sex = int(self.sex_input.text)
        cp = int(self.cp_input.text)
        trestbps = int(self.trestbps_input.text)
        chol = int(self.chol_input.text)
        fbs = int(self.fbs_input.text)
        restecg = int(self.restecg_input.text)
        thalach = int(self.thalach_input.text)
        exang = int(self.exang_input.text)
        oldpeak = float(self.oldpeak_input.text)
        slope = int(self.slope_input.text)
        ca = int(self.ca_input.text)
        thal = int(self.thal_input.text)
        
        input_list = [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]

        # make the prediction
        output = self.model.predict(input_list)

        # show the result
        if output[0] == 0:
            self.show_popup("Yaay !, You Dont Have Heart Disease","prediction Result")
        else:
            self.show_popup("Oops, You Have Heart Disease. lol","prediction Result")


if __name__ == '__main__':
   HeartDiseaseAppPredictor().run()