import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_probability = 1
    gene_num  = dict()

    parent_gene = [PROBS['gene'][0],PROBS['gene'][1],PROBS['gene'][2]]

    child_gene = [[[(1-PROBS['mutation'])*(1-PROBS['mutation']) , (1-PROBS['mutation'])*0.5 , (1-PROBS['mutation']) * PROBS['mutation']],
                    [(1-PROBS['mutation'])*0.5 , 0.5*0.5 , 0.5*PROBS['mutation']],
                    [(1-PROBS['mutation'])*PROBS['mutation'] , 0.5*PROBS['mutation'] , PROBS['mutation']*PROBS['mutation']]
                    ],
                [[2*(PROBS['mutation'] * (1-PROBS['mutation'])) , 0.5 , ((1-PROBS['mutation'])*(1-PROBS['mutation']))+(PROBS['mutation']*PROBS['mutation'])],
                    [ 0.5 , 2*(0.5 * 0.5) , 0.5],
                    [ ((1-PROBS['mutation'])*(1-PROBS['mutation']))+(PROBS['mutation']*PROBS['mutation']) , 0.5 , 2*((1-PROBS['mutation']) * PROBS['mutation'])]
                    ],
                [[ PROBS['mutation']*PROBS['mutation'] , PROBS['mutation']*0.5 , PROBS['mutation']*(1-PROBS['mutation'])],
                    [ PROBS['mutation']*0.5 , 0.5*0.5 , 0.5*(1-PROBS['mutation'])],
                    [ PROBS['mutation']*(1-PROBS['mutation']) , 0.5*(1-PROBS['mutation']) , (1-PROBS['mutation'])*(1-PROBS['mutation'])]
                    ]
                  ]
    
    traits_prob = [[ PROBS['trait'][0][False] , PROBS['trait'][1][False] , PROBS['trait'][2][False]],            
                  [ PROBS['trait'][0][True] , PROBS['trait'][1][True] , PROBS['trait'][2][True]]
                  ]    #have_trait[0]==No Trait , have_trait[1]=Trait

    for person in people:
        gene_num[person] = (2 if person in two_genes else
                          1 if person in one_gene else 0)
    #print(gene_num)
    for person in people:
        if people[person]['mother']==None and people[person]['father']==None:
            person_gene = parent_gene[gene_num[person]]
            trait = traits_prob[1][gene_num[person]] if person in have_trait else traits_prob[0][gene_num[person]]
        else:
            person_gene = child_gene[gene_num[person]][gene_num[people[person]['mother']]][gene_num[people[person]['father']]]
            trait = traits_prob[1][gene_num[person]] if person in have_trait else traits_prob[0][gene_num[person]]
        
        joint_probability *= (person_gene*trait)

        '''
            if person in two_genes:
                prob_2 = PROBS['gene'][2]
                have_trait = PROBS['traits'][2][True] if person in have_trait else PROBS['traits'][2][False]
                joint_probability *= (prob_2*have_trait)
                
            elif person in one_gene:
                prob_1 = PROBS['gene'][1]
                have_trait = PROBS['traits'][1][True] if person in have_trait else PROBS['traits'][1][False]
                joint_probability *= (prob_1*have_trait)

            else:
                prob_0 = PROBS['gene'][0]
                have_trait = PROBS['traits'][0][True] if person in have_trait else PROBS['traits'][0][False]
                joint_probability *= (prob_0*have_trait)
        '''

        
    return joint_probability
'''            
def child_genes_prob(child,gene,mother_gene,father_gene):
    prob = 0
    if gene == 0:
        if mother_gene ==0:
            if father_gene ==0:
                prob = (1-PROB['mutation']) * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = (1-PROB['mutation']) * 0.5
            elif father_gene ==2:
                prob = (1-PROB['mutation']) * PROB['mutation']
        elif mother_gene ==1:
            if father_gene ==0:
                prob = 0.5 * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = 0.5 * 0.5
            elif father_gene ==2:
                prob = 0.5 * PROB['mutation']
        elif mother_gene ==2:
            if father_gene ==0:
                prob = PROB['mutation'] * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = PROB['mutation'] * 0.5
            elif father_gene ==2:
                prob = PROB['mutation'] * PROB['mutation']

    elif gene == 1:   #needs to add one more aditional sum step
        if mother_gene ==0:
            if father_gene ==0:
                prob = PROB['mutation'] * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = PROB['mutation'] * 0.5
            elif father_gene ==2:
                prob = PROB['mutation'] * PROB['mutation']
        elif mother_gene ==1:
            if father_gene ==0:
                prob = 0.5 * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = 0.5 * 0.5
            elif father_gene ==2:
                prob = 0.5 * PROB['mutation']
        elif mother_gene ==2:
            if father_gene ==0:
                prob = (1-PROB['mutation']) * (1-PROB['mutation'])
            elif father_gene ==1:
                prob = (1-PROB['mutation']) * 0.5
            elif father_gene ==2:
                prob = (1-PROB['mutation']) * PROB['mutation']

    elif gene == 2:
        if mother_gene ==0:
            if father_gene ==0:
                prob = PROB['mutation'] * PROB['mutation']
            elif father_gene ==1:
                prob = PROB['mutation'] * 0.5
            elif father_gene ==2:
                prob = PROB['mutation'] * (1-PROB['mutation'])
        elif mother_gene ==1:
            if father_gene ==0:
                prob = 0.5 * PROB['mutation']
            elif father_gene ==1:
                prob = 0.5 * 0.5
            elif father_gene ==2:
                prob = 0.5 * (1-PROB['mutation'])
        elif mother_gene ==2:
            if father_gene ==0:
                prob = (1-PROB['mutation']) * PROB['mutation']
            elif father_gene ==1:
                prob = (1-PROB['mutation']) * 0.5
            elif father_gene ==2:
                prob = (1-PROB['mutation']) * (1-PROB['mutation'])
'''

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    gene_trait = dict()   #probabilities.fromkeys(probabilities,dict())
    
    for person in probabilities:
        gene_trait[person]={'gene': None,'trait':None}
        gene_trait[person]['gene'] = (2 if person in two_genes else
                                      1 if person in one_gene else 0)
        gene_trait[person]['trait'] = (True if person in have_trait else False)
    #print(gene_trait)

    for person in probabilities:
        probabilities[person]['gene'][gene_trait[person]['gene']] += p
        probabilities[person]['trait'][gene_trait[person]['trait']] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        total_gene = sum(probabilities[person]['gene'].values())
        total_trait = sum(probabilities[person]['trait'].values())
        
        for gene_num in probabilities[person]['gene']:
            probabilities[person]['gene'][gene_num] /= total_gene
            
        for trait in probabilities[person]['trait']:
            probabilities[person]['trait'][trait] /= total_trait


if __name__ == "__main__":
    main()
