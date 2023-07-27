def key_match(original,extracted):
    count=0
    for i in range(len(original)):
        if original[i]==extracted[i]:
            count+=1
    kpa = (count/len(original))*100
    return kpa

Original_Key=input("Enter the original key: ")
Extracted_Key_1=input("Enter the extracted key 1: ")
Extracted_Key_2=input("Enter the extracted key 2: ")
print("Key Prediction Accuracy 1 (KPA) is: ",key_match(Original_Key,Extracted_Key_1))
print("Key Prediction Accuracy 1 (KPA) is: ",key_match(Original_Key,Extracted_Key_2))




