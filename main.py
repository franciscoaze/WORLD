from random import randrange as rdm
import pandas as pd

id_seq = 0
n_areas = 6

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class Individual:
    global n_areas
    """
    Smallest organism 
    """

    def __init__(self, first_name, last_name, age, gender, id_seq, area=rdm(n_areas)):
        self.id = id_seq
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
        for person in pop.people:
            age_gap = abs(person.age - self.age)
            if (
                    self.partner == 'None' and person.partner == 'None' and person.area == self.area and person.gender != self.gender and person != self and age_gap <= 10 and person.age > 18 and self.age > 18):
                # candidate lives in the same area and is single
                if rdm(100) > 98:
                    self.partner = person
                    person.partner = self
                    # print(self.full_name,"found",self.partner.full_name,"!!")
                    return

    def give_birth(self, pop):
        # A woman can give birth if it has a partner, is over 20 and less than 35,
        if (self.partner != 'None' and self.age >= 20 and self.age < 36):
            if rdm(100) > 80:
                g = ['F', 'M']
                gender = rdm(2)
                first_name = pop.names.get_randomFirst(gender)
                last_name = self.last_name.split()[-1] + ' ' + self.partner.last_name.split()[-1]

                self.nr_children += 1
                return Individual(first_name, last_name, 1, g[gender], pop.id_seq, self.area)
                # ligar a pais
            else:
                return False
        else:
            return False


class Population:
    global n_areas
    """
    Group of Individuals
    """

    def __init__(self, start_indiviudals=50):
        self.people = []
        self.names = names()
        self.id_seq = 1
        self.nr_people = 0
        g = ['F', 'M']
        for i in range(start_indiviudals):
            # Female is 0, Male is 1
            gender = rdm(2)
            first_name = self.names.get_randomFirst(gender)
            last_name = self.names.get_randomLast()
            age = rdm(15, 50)

            new_person = Individual(first_name, last_name, age, g[gender], self.id_seq, rdm(n_areas))
            self.people.append(new_person)
            self.id_seq += 1
            self.nr_people += 1

    def socialize(self):
        for person in self.people:
            # ----- find mechanism to associate probability to socialiaze
            person.find_partner(self)

    def pop_growth(self):
        for person in self.people:
            if person.gender == 'F':
                new_person = person.give_birth(self)
                if new_person != False:
                    # print(new_person.full_name + ' was born!')
                    new_person.parent.extend([person, person.partner])
                    self.people.append(new_person)
                    self.id_seq += 1
                    person.children.append(new_person)
                    person.partner.children.append(new_person)

    def aging(self, factor=1):
        for person in self.people:
            person.age += factor
            if person.age > 80 and rdm(100) > 75:
                # Person dies
                self.people.remove(person)
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

    def show(self):
        return self.df.loc[:, ['full_name', 'age', 'gender', 'nr_children', 'partner', 'area']]

    def find(self, id):
        return self.df.loc[id]

    def stats(self):
        nr_people = w.df.shape[0]
        per_partner = 100 * (nr_people - self.df['partner'].value_counts()['None']) / nr_people
        print('\nInfo for cycle ' + str(self.nr_cycle))
        print('Population Size: ' + str(nr_people))
        print('Percentage of Married: ' + str(per_partner) + '%')
        M = self.df['gender'].value_counts()['M']
        F = self.df['gender'].value_counts()['F']
        print('M: ' + str(M) + ' | F: ' + str(F))
        print('Mean Age: ' + str(self.df['age'].mean()))

    def update_pop(self):
        self.df = pd.DataFrame([p.__dict__ for p in self.pop.people])
        self.df = self.df.set_index('id')

    def iterate(self, times):
        for i in range(times):
            # Corresponds to one iteration of the life cycle. Could be day, month, year...
            # The different world mechanisms are activated here.
            self.nr_cycle += 1
            # Mechanism 3 - Increase age
            self.pop.aging(1)

            print('===Cycle nr. ' + str(self.nr_cycle) + '===')
            # Mechnism 1 - Finding a partner
            self.pop.socialize()

            # Mechanism 2 - Population growth
            self.pop.pop_growth()

        # Update df
        self.update_pop()
        # self.stats()


class names:
    def __init__(self, start_indiviudals=10):
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