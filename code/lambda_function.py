import json
import numpy as np
import pandas as pd



def lambda_handler(event, context):
  #reading in data
  maxPrice = int(event["maxPrice"])
  userInputs = ["house" + event["householdSize"].upper(), "commute" + event["dailyCommute"].upper(),
                event["ecoFriendly"].upper(), event["luxuryChoice"].upper()]
  
  feat = pd.read_csv("Data/Features/featuresData.csv", na_filter = False)
  feat = feat.loc[feat["MSRP"] <= maxPrice]
  feat.index = [i for i in range(len(feat))]
    
  
  #percents derived from eda
  stylePercents = {"houseY": {"regular car": 33, "van": 39, "truck": 17, "sport car": 2, "station wagon": 8},
                  "houseN": {"regular car": 55, "van": 15, "truck": 21, "sport car": 5, "station wagon": 4},
                  "commuteY": {"regular car": 55, "van": 20, "truck": 17, "sport car": 4, "station wagon": 4},
                  "commuteN": {"regular car": 44, "van": 23, "truck": 22, "sport car": 5, "station wagon": 6}}

  fuelPercents = {"houseY": {"gasoline": 32, "electric": 27, "other": 41},
                  "houseN": {"gasoline": 36, "electric": 27, "other": 37},
                  "commuteY": {"gasoline": 28, "electric": 30, "other": 42},
                  "commuteN": {"gasoline": 40, "electric": 25, "other": 35}}
                

  sizePercents = {"houseY": {"midsize/large": 67, "compact": 33},
                  "houseN": {"midsize/large": 56, "compact": 44},
                  "commuteY": {"midsize/large": 62, "compact": 38},
                  "commuteN": {"midsize/large": 57, "compact": 43}}


  styleDict = {"regular car": ["Sedan", "SUV", "Hatchback"],
              "van": ["Minivan"],
              "truck": ["Pickup"],
              "sport car": ["Coupe", "Convertible"],
              "station wagon": ["Station Wagon"]}

  fuelDict = {"gasoline": ["regular", "premium", "diesel"],
              "electric": ["electric"],
              "other": ["natural gas", "flex-fuel"]}

  sizeDict = {"midsize/large": ["Midsize/Large"],
              "compact": ["Compact"]}
              
              
  def getCategory(inputStr, inputDict):
    for key, value in inputDict.items():
      for elem in value:
        if elem in inputStr:
          return key

  #makes the results slightly random for better usability
  def probScore(prob):
    if np.random.randint(1, 101) <= prob:
      return 0.8
    else:
      return 0.2

  def removeNA(inputList):
      return [elem for elem in inputList if elem != "N/A"]


  hpList = list(map(float, removeNA(feat["Engine HP"])))
  hp75, hp25 = np.percentile(hpList, [75]), np.percentile(hpList, [25])
  
  highwayList = list(map(float, removeNA(feat["Highway MPG"])))
  highway75, highway25 = np.percentile(highwayList, [75]), np.percentile(highwayList, [25])
  
  cityList = list(map(float, removeNA(feat["City MPG"])))
  city75, city25 = np.percentile(cityList, [75]), np.percentile(cityList, [25])


  ecoCoeff, ecoUnit = 0.15, 0.1
  ecoWords = ["natural gas", "flex-fuel", "electric", "Hybrid"]
  
  #scores ecofriendliness of a car
  def ecoScore(carInfo):
    score, ecoCount = 0, 0
  
    for i in range(3):
      if isinstance(carInfo[3], str) and ecoWords[i] in carInfo[3]:
        ecoCount += 1
    
    if isinstance(carInfo[9], str) and ecoWords[3] in carInfo[9]:
      ecoCount += 1
  
    score = ecoCount * ecoCoeff
  
    if carInfo[4] != "N/A" and float(carInfo[4]) > hp75:
      score -= ecoUnit
    elif carInfo[4] != "N/A" and float(carInfo[4]) < hp25:
      score += ecoUnit
  
    if carInfo[5] != "N/A" and float(carInfo[5]) > 8:
      score -= ecoUnit
    elif carInfo[5] != "N/A" and float(carInfo[5]) <= 4:
      score += ecoUnit
  
    if float(carInfo[12]) > highway75:
      score += ecoUnit
    elif float(carInfo[12]) < highway25:
      score -= ecoUnit
  
    if float(carInfo[12]) > city75:
      score += ecoUnit
    elif float(carInfo[12]) < city25:
      score -= ecoUnit
  
    if "premium" in carInfo[3] and "flex-fuel" not in carInfo[3]:
      score -= ecoUnit
  
    return score
    
    
  luxuryCoeff, luxuryUnit = 0.15, 0.05
  luxuryWords = ["Crossover", "Exotic", "High-Performance", "Luxury"]
  
  #scores how luxurious a car is
  def luxuryScore(carInfo):
    score, luxuryCount = 0, 0
  
    for i in range(len(luxuryWords)):
      if isinstance(carInfo[9], str) and luxuryWords[i] in carInfo[9]:
        luxuryCount += 1
    
    score = luxuryCount * luxuryCoeff
  
    if carInfo[4] != "N/A" and float(carInfo[4]) > hp75:
      score += luxuryUnit
    elif carInfo[4] != "N/A" and float(carInfo[4]) < hp25:
      score -= luxuryUnit
  
    if carInfo[5] != "N/A" and float(carInfo[5]) > 8:
      score += luxuryUnit
    elif carInfo[5] != "N/A" and float(carInfo[5]) <= 4:
      score -= luxuryUnit
  
    if float(carInfo[12]) > highway75:
      score -= luxuryUnit
    elif float(carInfo[12]) < highway25:
      score += luxuryUnit
  
    if float(carInfo[12]) > city75:
      score -= luxuryUnit
    elif float(carInfo[12]) < city25:
      score += luxuryUnit
  
    if "Convertible" in carInfo[11] or "Coupe" in carInfo[11]:
      score += luxuryUnit * 4
  
    return score


  #scores car based on a variety of criteria
  def scoreCar(carInfo):
    score = 0
  
    style = getCategory(carInfo[11], styleDict)
    fuel = getCategory(carInfo[3], fuelDict)
    size = getCategory(carInfo[10], sizeDict)
  
    for i in range(2):
      score += probScore(stylePercents[userInputs[i]][style])
      score += probScore(fuelPercents[userInputs[i]][fuel])
      score += probScore(sizePercents[userInputs[i]][size])
  
    score += carInfo[14] / 10000
  
    if carInfo[6] == "manual" or carInfo[6] == "automated manual":
      score *= 0.7
  
    if userInputs[2] == "Y":
      score += ecoScore(carInfo)
  
    if userInputs[3] == "Y":
     score += luxuryScore(carInfo)
  
    if carInfo[2] >= 2015:
      score *= 1.2
  
    if carInfo[15] >= maxPrice - 5000:
      score *= 1.3
  
    return score
    

  #scores all cars
  def scoreAll(feat):
    feat["Score"] = feat.apply(scoreCar, axis = 1)
    return dict(zip(list(feat["Score"]), list(feat.index)))


  #sorts scored cars
  scoreIndexDict = scoreAll(feat)
  allScores = list(scoreIndexDict.keys())
  allScores.sort(reverse = True)
  
  normScores = list((np.array(allScores) - min(allScores)) / (max(allScores) - min(allScores)) * 10)


  topNames, topScores, topInfo, bottomNames, bottomScores, bottomInfo = [], [], [], [], [], []
  
  #finds top and bottom 5 cars
  for i in range(5):
    topList = list(feat.iloc[scoreIndexDict[allScores[i]]])
    bottomList = list(feat.iloc[scoreIndexDict[allScores[len(allScores) - 1 - i]]])
    
    topNames.append("{year} {make} {model} {carType}".format(year = str(topList[2]), make = topList[0], model = topList[1], carType = topList[11]))
    topScores.append(str(round(normScores[i], 2)))
    
    bottomNames.append("{year} {make} {model} {carType}".format(year = str(bottomList[2]), make = bottomList[0], model = bottomList[1], carType = bottomList[11]))
    bottomScores.append(str(round(normScores[len(allScores) - 1 - i], 2)))


  return {
        "statusCode": 200,
        "names": topNames,
        "scores": topScores
         }