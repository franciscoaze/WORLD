from random import randrange as rdm
import pandas as pd
from tools import measure
import xlsxwriter
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.widgets import Slider

# TODO adicionar novas caraceristcas às pessoas
# TODO adicionar outros graficos: piramide populacional F/M
# TODO algum tipo de ligacao a internet
# TODO algum tipo de ligacao com um ficheiro batch tipo ligar de x em x tempo
# TODO Catastrofes
# TODO Genetic algorithm?
# TODO Tentar criar nós independentes / microserviços?

id_seq = 0
n_areas = 6

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 10)


class Individual:
    global n_areas
    """
    Smallest organism 
    """

    def __init__(self, first_name, last_name, age, gender, id_seq1, area=rdm(n_areas)):
        self.id = id_seq1
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = first_name + " " + last_name
        self.gender = gender
        self.age = age
        self.partner = 'None'
        self.area = area
        self.children = []
        self.nr_children = 0
        self.parent = []
        self.status = 'Alive'

    def __repr__(self):
        return self.full_name + "[" + str(self.id) + "]"

    def relocate(self, new_area=rdm(n_areas)):
        return new_area

    def show_info(self):
        print("Name: " + self.full_name)
        print("Age: " + str(self.age) + " years old")
        print("Gender: " + self.gender)
        print("Partner: " + str(self.partner))
        print("Area Code: " + str(self.area))

    def find_partner(self, pop):
        for person in pop.singles_list:
            age_gap = abs(person.age - self.age)
            if (person.area == self.area and person.gender != self.gender and person != self and age_gap <= 10 and person.age > 18 and self.age > 18):
                # candidate lives in the same area and is single
                if rdm(100) > pop.partner_prob:
                    self.partner = person
                    person.partner = self
                    # print(self.full_name,"found",self.partner.full_name,"!!")
                    return True
        return False

    def give_birth(self, pop):
        # A woman can give birth if it has a partner, is over 20 and less than 35,
        if rdm(100) > pop.birth_prob:
            g = ['F', 'M']
            gender = rdm(2)
            first_name = pop.names.get_randomFirst(gender)
            last_name = self.last_name.split()[-1] + ' ' + self.partner.last_name.split()[-1]

            return Individual(first_name, last_name, 1, g[gender], pop.id_seq, self.area)
        else:
            return False


class Population:
    global n_areas
    """
    Group of Individuals
    """

    def __init__(self, start_indiviudals=50):
        self.people = []
        self.singles_list = []
        self.names = names()
        self.id_seq = 1
        self.nr_people = 0

        self.partner_prob = 95
        self.birth_prob = 70

        g = ['F', 'M']
        for i in range(start_indiviudals):
            # Female is 0, Male is 1
            gender = rdm(2)
            first_name = self.names.get_randomFirst(gender)
            last_name = self.names.get_randomLast()
            age = rdm(15, 50)

            new_person = Individual(first_name, last_name, age, g[gender], self.id_seq, rdm(n_areas))
            self.people.append(new_person)
            self.singles_list.append(new_person)
            self.id_seq += 1
            self.nr_people += 1

    def socialize(self):
        for person in self.singles_list:
            # ----- find mechanism to associate probability to socialize
            if person.find_partner(self):
                self.singles_list.remove(person.partner)
                self.singles_list.remove(person)

    def pop_growth(self):
        for person in self.people:
            if person.gender == 'F' and person.partner != 'None' and person.age >= 20 and person.age < 36:
                new_person = person.give_birth(self)
                if new_person != False:
                    # print(new_person.full_name + ' was born!')
                    new_person.parent.extend([person, person.partner])
                    self.people.append(new_person)
                    self.id_seq += 1

                    person.nr_children += 1
                    person.partner.nr_children+=1
                    person.children.append(new_person)
                    person.partner.children.append(new_person)

                    self.nr_people += 1

    def aging(self, factor=1):
        for person in self.people:
            person.age += factor
            if person.age > 20 and person not in self.singles_list:
                self.singles_list.append(person)
            if person.age > 80 and rdm(100) > 75:
                # Person dies
                self.people.remove(person)
                try:
                    self.singles_list.remove(person)
                except:
                    pass
                self.nr_people -= 1

                person.status = 'Dead'
                # print(person.full_name+'['+str(person.id)+'] has died...')
                if not isinstance(person.partner, str):
                    person.partner.partner = 'None'


class World:
    def __init__(self):
        self.pop = Population(200)
        self.df = pd.DataFrame([p.__dict__ for p in self.pop.people])
        self.df = self.df.set_index('id')
        self.nr_cycle = 0

        plt.close()
        plt.style.use('dark_background')

        self.fig, [self.ax1,self.ax2]= plt.subplots(1,2)
        plt.subplots_adjust(bottom=0.25)
        self.line, = self.ax1.plot([],[])
        self.ydata = []
        self.ax1.grid(color='grey')
        axprob1 = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='grey')
        axprob2 = plt.axes([0.2, 0.15, 0.65, 0.03], facecolor='grey')
        self.sprob1 = Slider(axprob1, 'Birth Prob', 0, 1, valinit=0.1)
        self.sprob2 = Slider(axprob2, 'Partner Prob', 0, 1, valinit=0.1)
        self.sprob1.on_changed(self.update_properties_birth)
        self.sprob2.on_changed(self.update_properties_partner)

        # self.axes = plt.gca()
        # self.axes.set_ylim(0,1000)
        # self.axes.set_xlim(0,200)
        # self.line, = self.axes.plot([],[],'r-')
        # self.ydata = []
        # plt.subplots_adjust(bottom=0.2)
        # plt.show()

    def update_properties_birth(self,val):
        self.pop.birth_prob = 100-(100*val)

    def update_properties_partner(self,val):
        self.pop.partner_prob = 100-(100*val)

    def show(self):
        return self.df.loc[:, ['full_name', 'age', 'gender', 'nr_children', 'partner', 'area']]

    def find(self, id):
        return self.df.loc[id]

    def stats(self):
        per_partner = 100 * (self.pop.nr_people - self.df['partner'].value_counts()['None']) / self.pop.nr_people
        print('\nInfo for cycle ' + str(self.nr_cycle))
        print('Population Size: ' + str(self.pop.nr_people))
        print('Percentage of Married: ' + str(per_partner) + '%')
        M = self.df['gender'].value_counts()['M']
        F = self.df['gender'].value_counts()['F']
        print('M: ' + str(M) + ' | F: ' + str(F))
        print('Mean Age: ' + str(self.df['age'].mean()))

    def update_pop(self):
        self.df = pd.DataFrame([p.__dict__ for p in self.pop.people])
        self.df = self.df.set_index('id')
        try:
            self.df.to_excel('population.xlsx')
        except Exception:
            print('Could not save dataframe. Please close the file.')

    @measure
    def iterate(self, times):
        for i in range(times):
            # Corresponds to one iteration of the life cycle. Could be day, month, year...
            # The different world mechanisms are activated here.
            self.nr_cycle += 1
            # Mechanism 3 - Increase age
            self.pop.aging(1)

            print('===Cycle nr. ' + str(self.nr_cycle) + '===')
            # Mechanism 1 - Finding a partner
            self.pop.socialize()

            # Mechanism 2 - Population growth
            self.pop.pop_growth()

            self.plotGeneration(self.pop.nr_people)
            self.df = pd.DataFrame([p.__dict__ for p in self.pop.people])
            self.ax2.cla()
            kwargs = {'rwidth':0.7}
            self.df['age'].hist(ax=self.ax2,grid=False,bins=np.arange(0,101,10),**kwargs)

        # Update df
        self.update_pop()
        # self.stats()

    def plotGeneration(self,new_data):
        self.ax1.set_ylim(0,new_data+100)
        self.ax1.set_xlim(0,self.nr_cycle+50)
        self.ydata.append(new_data)
        self.line.set_ydata(self.ydata)
        self.line.set_xdata(range(self.nr_cycle))
        plt.draw()
        plt.pause(1e-17)

class names:
    def __init__(self):
        f1 = open("first_namesM.txt")
        f2 = open("first_namesF.txt")
        l = open("last_names.txt")
        self.first_namesM = f1.read().split('\n')
        self.first_namesF = f2.read().split('\n')
        self.nr_Fnames = len(self.first_namesM)
        self.last_names = l.read().split('\n')
        self.nr_Lnames = len(self.last_names)
        f1.close()
        f2.close()
        l.close()

    def get_randomFirst(self, gender):
        # Female is 0, Male is 1
        if gender:
            return self.first_namesM[rdm(self.nr_Fnames)].title()
        else:
            return self.first_namesF[rdm(self.nr_Fnames)]

    def get_randomLast(self):
        return self.last_names[rdm(self.nr_Lnames)]


w = World()