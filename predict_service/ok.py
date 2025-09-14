import requests

# Test with files
files = {
    'file': open(r'patients_test/Mild_Cardiac_Insufficiency/patient_classe_0_020.dat', 'rb'),
    'hea': open(r'patients_test/Mild_Cardiac_Insufficiency/patient_classe_0_020.hea', 'rb')
}
response = requests.post('http://127.0.0.1:5000/predict', files=files)
print(response.json())

#Test with array
# json_data = {"array": [0.1, 0.2, 0.3, 0.4, 0.5]}
# response = requests.post('http://127.0.0.1:5000/predict', json=json_data)
# print(response.json())


