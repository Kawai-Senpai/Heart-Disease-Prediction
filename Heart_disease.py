import pickle

def get_input():
    age = int(input("Enter your age: "))
    sex = int(input("Enter your sex (0 for female, 1 for male): "))
    cp = int(input("Enter your chest pain type (0 for typical angina, 1 for atypical angina, 2 for non-anginal pain, 3 for asymptomatic): "))
    trestbps = int(input("Enter your resting blood pressure (in mm Hg on admission to the hospital): "))
    chol = int(input("Enter your serum cholestoral in mg/dl: "))
    fbs = int(input("Enter your fasting blood sugar level (1 if > 120 mg/dl, 0 otherwise): "))
    restecg = int(input("Enter your resting electrocardiographic results (0 for normal, 1 for having ST-T wave abnormality, 2 for showing probable or definite left ventricular hypertrophy): "))
    thalach = int(input("Enter your maximum heart rate achieved: "))
    exang = int(input("Enter whether you experience exercise-induced angina (1 for yes, 0 for no): "))
    oldpeak = float(input("Enter your ST depression induced by exercise relative to rest: "))
    slope = int(input("Enter the slope of your peak exercise ST segment (0 for upsloping, 1 for flat, 2 for downsloping): "))
    ca = int(input("Enter the number of major vessels colored by flourosopy (0-3): "))
    thal = int(input("Enter your thalassemia type (1 for fixed defect, 2 for normal, 3 for reversible defect): "))
    
    input_list = [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
    
    return input_list

#importing the model
with open('engine.CookieNeko', 'rb') as file:
    model = pickle.load(file)

#Predicting
example_input = get_input()
output = model.predict(example_input)

if(output[0]==0):
    print("No, You don't have Heart Disease")
else:
    print("You Have Heart Disease")