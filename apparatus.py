'''

log:
    fact-name a b halfLife last created

attempts:
    fact-id (attemptDate, attemptResult)


'''

from datetime import datetime, timedelta
import ebisu

defaultModel = (4., 4., 24.)

facts = {}

now = datetime.now()
oneHour = timedelta(hours=1)

with open('facts.txt') as factsFile:
    for i, row in enumerate(factsFile.readlines()):
        id, name, a, b, hl, lastTest, crDate = row.split()
        a, b, hl = float(a), float(b), float(hl)
        lastTest = datetime.fromtimestamp(float(lastTest))
        crDate = datetime.fromtimestamp(float(crDate))
        facts[id] = dict(
            id=id,
            name=name,
            model=(a, b, hl),
            lastTest=lastTest,
            crDate=crDate,
        )
 
facts_sorted = []

def sortFacts():   
    global facts_sorted
    now = datetime.now()
    for id, fact in facts.items():
        fact['recall'] = ebisu.predictRecall(fact['model'], 
            (now - fact['lastTest']) / oneHour,
            exact=True)
        facts[id] = fact
    facts_sorted = sorted([*facts.values()], key=lambda f: f['recall'])

import os
cls = lambda: os.system('cls')

def printAllFacts(facts):
    cls()
    for i, fact in enumerate(facts_sorted):
        if i > 9:
            print(f'... ({len(facts) - i} more)')
            break 
        print("{:.2f}%".format(fact['recall'] * 100), fact['id'], fact['name'])
        
def processFact(fact):
    cls()
    print(f'ID={fact["id"]} {fact["name"]} \n')
    cmd = input('Your choice (default="revert"): ')
    if not cmd:
        return
    else:
        result, times = cmd.split()
        result, times = float(result), int(times)
        newModel = ebisu.updateRecall(fact['model'],
                              result,
                              times,
                              (now - fact['lastTest']) / oneHour)
        fact['model'] = newModel
        fact['lastTest'] = datetime.now()
        fact['recall'] = ebisu.predictRecall(
            newModel, 
            0,
            exact=True)
        facts[fact['id']] = fact
    sortFacts()        
       
datetime.now().timestamp
       
def saveFacts():
    with open('facts.txt', 'w') as file:
        for fact in [*facts.values()]:
            a, b, hl = fact['model']
            file.write(
                f"{fact['id']} {fact['name']} {a} {b} {hl} {fact['lastTest'].timestamp()} {fact['crDate'].timestamp()}\n"
            )
            
def addNewFact():
    try:
        cls()
        id = input('ID: ')
        name = input('Name: ')
        fact = dict(
            id=id, name=name, model=defaultModel, lastTest=datetime.now(), crDate=datetime.now(), recall=1
        )
        facts[id] = fact
    except:
        pass
try: 
    while True:
        sortFacts()
        printAllFacts(facts)
        cmd = input('\nYour choice (default="nxt"): ')
        if not cmd or cmd == 'nxt':
            processFact(facts_sorted[0])
        elif cmd in facts:
            processFact(facts[cmd])
        elif cmd == 'new':
            addNewFact()
        elif cmd == 'exit':
            saveFacts()
            break
except:
    saveFacts()
