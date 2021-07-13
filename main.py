import numpy as np
import cv2 as cv
from google.colab.patches import cv2_imshow
import matplotlib.pyplot as plt
import random
import operator
from copy import deepcopy

#load the image as a cv object
img=cv.imread('/content/painting.png')
cv.imshow(img)
print(img.shape)

#define useful classes
class Gene:
  def __init__(self,center,radius,rgb,alpha):
    self.center=tuple(center)
    self.radius=radius
    self.rgb=(int(rgb[0]),int(rgb[1]),int(rgb[2]))
    self.alpha=alpha

class ind:
  def __init__(self,genes,fitness):
    self.genes=genes
    self.fitness=fitness


class Population:
  def __init__(self,inds,elites):
    self.inds=inds
    self.elites=elites




#initialize population with individuals with randomized genes
def pop_init(num_inds, num_genes):
    inds = []
    elites = []
    for i in range(num_inds):
        genes = []
        for j in range(num_genes):
            gene = Gene(np.random.random_integers(img.shape[0], size=2),
                        int(random.random() * (img.shape[0] / 2)), np.random.random_integers(255, size=3),
                        random.random())
            genes.append(gene)
        genes.sort(key=operator.attrgetter('radius'), reverse=True)
        temp_ind = ind(genes, 0)
        inds.append(temp_ind)
    return Population(inds, elites)




#evaluate an individual to assign it a fitness value
def evaluate_ind(indv):
    gen_img = np.ones(img.shape, dtype='uint8') * 255
    indv.genes.sort(key=operator.attrgetter('radius'), reverse=True)
    for gene in indv.genes:
        alpha = gene.alpha
        overlay = deepcopy(gen_img)
        cv.circle(overlay, gene.center, gene.radius, gene.rgb, -1)
        gen_img = overlay * alpha + gen_img * (1 - alpha)

    fitness = -np.sum(np.square(img - gen_img))
    return fitness

#apply tournament selection to the population
def selection(pop,num_elites,tm_size,num_parents):
  ind_list=pop.inds.copy()
  #sort the individuals based on their fitnesses
  ind_list.sort(key=operator.attrgetter('fitness'),reverse=True)
  elites=[]
  passed_inds=[]
  #seperate the elites from the others
  for i in range(num_elites):
    elites.append(ind_list.pop(i))
  np.random.shuffle(ind_list)
  #apply tournament selection
  while (len(passed_inds)<num_parents):
    indices=np.random.random_integers(len(ind_list)-1,size=tm_size)
    selected_inds=np.array(ind_list)[indices]
    sorted(selected_inds,key=operator.attrgetter('fitness'))
    if(selected_inds[0] not in passed_inds):
     passed_inds.append(selected_inds[0])
  return [elites,passed_inds]


#apply crossover to a bunch of selected individuals
def crossover(inds, num_children):
    if (len(inds) % 2 == 1):
        last = inds.pop(-1)
    new_inds = []
    for i in range(0, num_children, 2):
        parent1 = inds[i]
        parent2 = inds[i + 1]
        child1_genes = []
        child2_genes = []
        for gene1, gene2 in zip(parent1.genes, parent2.genes):
            if (random.random() > 0.5):
                child1_genes.append(gene1)
                child2_genes.append(gene2)
            else:
                child1_genes.append(gene2)
                child2_genes.append(gene1)
        new_inds.append(ind(child1_genes, 0))
        new_inds.append(ind(child2_genes, 0))
    return new_inds

#apply mutation to an individual among the the two types of mutations
def mutation(gene,mutation_prob,mutation_type):
  prob=random.random()
  if(prob<mutation_prob):
    if(mutation_type=="unguided"):
      gene.center=(random.randint(0,180),random.randint(0,180))
      gene.radius=random.randint(0,90)
      gene.rgb=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      gene.alpha=random.random()
    elif(mutation_type=="guided"):
      gene.center=(random.randint(max(gene.center[0]-img.shape[0]//4,0),min(gene.center[0]+img.shape[0]//4,img.shape[0])),
      random.randint(max(gene.center[0]-img.shape[0]//4,0),min(gene.center[0]+img.shape[0]//4,img.shape[0])))
      gene.radius=random.randint(max(0,gene.radius-10),min(gene.radius+10,90))
      gene.rgb=(random.randint(max(0,gene.rgb[0]-64),min(gene.rgb[0]+64,255)),
      random.randint(max(0,gene.rgb[0]-64),min(gene.rgb[0]+64,255)),
      random.randint(max(0,gene.rgb[0]-64),min(gene.rgb[0]+64,255)))
      gene.alpha=random.uniform(max(0,gene.alpha-0.25),min(1,gene.alpha+0.25))
  return gene


#main loop

# set hyperparameters
num_inds = 20
num_genes = 50
tm_size = 5
mutation_prob = 0.2
mutation_type = "unguided"
num_generations = 1000
frac_elites = 0.2
frac_parents = 0.6

# initialize the population
fitness_curve = []

for frac_elites in [0.05, 0.4]:
    pop = pop_init(num_inds, num_genes)
    for generation in range(num_generations):
        # evaluate all individuals
        for indv in pop.inds:
            indv.fitness = evaluate_ind(indv)

        num_elites = int(frac_elites * len(pop.inds))
        num_parents = int(frac_parents * len(pop.inds))

        # apply selection
        pop.elites, selected_inds = selection(pop, num_elites, tm_size, num_parents)

        # display the closest image to the source image within a generation
        best_img = np.ones(img.shape, dtype='uint8') * 255
        best_genes = pop.elites[0].genes

        if (generation % 100 == 99 or generation == 0):
            best_img = np.ones(img.shape, dtype='uint8') * 255
            best_genes = pop.elites[0].genes
            print("Best of generation ", generation + 1)
            for best_gene in best_genes:
                best_alpha = best_gene.alpha
                overlay = deepcopy(best_img)
                cv.circle(overlay, best_gene.center, best_gene.radius, best_gene.rgb, -1)
                best_img = overlay * best_alpha + best_img * (1 - best_alpha)
            cv2_imshow(best_img)

        num_children = len(pop.inds) - num_elites - num_parents

        # apply crossover
        new_inds = crossover(selected_inds, num_children)
        # merge th echildren and parents
        all_inds = selected_inds + new_inds
        # apply mutation
        for indv in all_inds:
            for gene in indv.genes:
                gene = mutation(gene, mutation_prob, mutation_type)

        pop.inds = pop.elites + all_inds
        fitness_curve.append(-pop.elites[0].fitness)