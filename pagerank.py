import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    print(corpus)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    corpus_len = len(corpus)
    page_len= len(corpus[page])
    
    model = dict()
    
    additional_prob = (1-damping_factor)/corpus_len
    if page_len ==0:
        page_len = corpus_len
        corpus[page] = corpus.keys()
    prob = damping_factor/page_len
    
    for i in corpus:
        model[i] = additional_prob
    for j in corpus[page]:
        model[j] += prob
                
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    
    for i in corpus:
        pagerank[i] = 0    
    weights = [0]*len(corpus)
    count = n
    while count != 0:
        count -= 1
        sample = random.choices(list(corpus),weights)[0]
        weights = list(transition_model(corpus,sample,damping_factor).values())
        pagerank[sample] = pagerank[sample] + 1
        
    for i in pagerank:
        pagerank[i] /= n
        
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
     # Initialize constants and lists
    converge = 0.001
    diff = 1
    
    N = len(corpus)
    d = damping_factor
    total_page = list(corpus.keys())
    
    # Set all intial values of pagerank
    pagerank = {k: 1 / N for k in corpus.keys()}
    
    # Loops until the values converge
    while (diff > converge):
        # Loops through pages and calculates first section of PageRank equation
        for page in total_page:
            past_step = pagerank[page]
            pagerank[page] = ((1 - d) / N)
            
            # For each page, loops through links to that page and calculates second section of PageRank equation
            for i in total_page:
                sum_i = 0
                p = corpus[i]
                
                if len(page) == 0:
                    p = total_page
                    
                if page in p:
                    sum_i += pagerank[i] / len(p)                
                pagerank[page] += (d * sum_i)            
            
            # Calculates the different between past step and current value (checks for convergence)
            diff = abs(pagerank[page] - past_step)
    total = sum(pagerank.values())
    for i in pagerank:
        pagerank[i] /= total
            
    return pagerank


if __name__ == "__main__":
    main()
